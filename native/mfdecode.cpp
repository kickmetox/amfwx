#include <windows.h>
#include <mfapi.h>
#include <mfidl.h>
#include <mfreadwrite.h>
#include <cstdio>
#include <vector>
#include <map>
#include <mutex>
#include <propvarutil.h>

#pragma comment(lib, "mfplat.lib")
#pragma comment(lib, "mfreadwrite.lib")
#pragma comment(lib, "mfuuid.lib")
#pragma comment(lib, "ole32.lib")

struct MFReader {
    IMFSourceReader* reader;
    UINT32 width;
    UINT32 height;
};

static std::map<int, MFReader*> readers;
static std::map<int, MFReader*> audioReaders;
static std::mutex readerMutex;
static int nextHandle = 1;

extern "C" __declspec(dllexport)
int mf_open(const wchar_t* path, int* width, int* height)
{
    MFStartup(MF_VERSION);
    IMFSourceReader* reader = nullptr;
    IMFAttributes* attributes = nullptr;
    MFCreateAttributes(&attributes, 1);
    attributes->SetUINT32(MF_SOURCE_READER_ENABLE_VIDEO_PROCESSING, TRUE);
    HRESULT hr = MFCreateSourceReaderFromURL(path, attributes, &reader);
    attributes->Release();
    if (FAILED(hr) || !reader) return -1;
    IMFMediaType* type = nullptr;
    MFCreateMediaType(&type);
    type->SetGUID(MF_MT_MAJOR_TYPE, MFMediaType_Video);
    type->SetGUID(MF_MT_SUBTYPE, MFVideoFormat_NV12);
    hr = reader->SetCurrentMediaType(MF_SOURCE_READER_FIRST_VIDEO_STREAM,
                                     nullptr, type);
    type->Release();
    if (FAILED(hr)) { reader->Release(); return -2; }
    IMFMediaType* current = nullptr;
    reader->GetCurrentMediaType(MF_SOURCE_READER_FIRST_VIDEO_STREAM, &current);
    UINT32 w = 0, h = 0;
    if (current) {
        MFGetAttributeSize(current, MF_MT_FRAME_SIZE, &w, &h);
        current->Release();
    }
    *width = (int)w;
    *height = (int)h;
    std::lock_guard<std::mutex> lock(readerMutex);
    int handle = nextHandle++;
    readers[handle] = new MFReader{reader, w, h};
    return handle;
}

extern "C" __declspec(dllexport)
int mf_next(int handle, unsigned char* output, int output_size,
            int* width, int* height, int* stride)
{
    std::lock_guard<std::mutex> lock(readerMutex);
    auto found = readers.find(handle);
    if (found == readers.end()) return -1;
    MFReader* state = found->second;
    DWORD flags = 0;
    IMFSample* sample = nullptr;
    HRESULT hr = state->reader->ReadSample(MF_SOURCE_READER_FIRST_VIDEO_STREAM,
                                           0, nullptr, &flags, nullptr,
                                           &sample);
    if (FAILED(hr) || (flags & MF_SOURCE_READERF_ENDOFSTREAM)) {
        if (sample) sample->Release();
        return 0;
    }
    int copied = -2;
    if (sample) {
        IMFMediaBuffer* buffer = nullptr;
        if (SUCCEEDED(sample->ConvertToContiguousBuffer(&buffer)) && buffer) {
            BYTE* data = nullptr;
            DWORD length = 0;
            if (SUCCEEDED(buffer->Lock(&data, nullptr, &length))) {
                int pitch = (int)(state->width * 3 / 2);
                int needed = pitch * (int)state->height;
                if (needed <= output_size && length >= (DWORD)needed) {
                    memcpy(output, data, needed);
                    copied = needed;
                    *stride = pitch;
                }
                buffer->Unlock();
            }
            buffer->Release();
        }
        sample->Release();
    }
    *width = (int)state->width;
    *height = (int)state->height;
    return copied;
}

extern "C" __declspec(dllexport)
int mf_seek(int handle, double seconds)
{
    std::lock_guard<std::mutex> lock(readerMutex);
    auto found = readers.find(handle);
    if (found == readers.end()) return -1;
    PROPVARIANT position;
    PropVariantInit(&position);
    position.vt = VT_I8;
    position.hVal.QuadPart = (LONGLONG)(seconds * 10000000.0);
    HRESULT hr = found->second->reader->SetCurrentPosition(GUID_NULL, position);
    PropVariantClear(&position);
    return SUCCEEDED(hr) ? 0 : -2;
}

extern "C" __declspec(dllexport)
void mf_close(int handle)
{
    std::lock_guard<std::mutex> lock(readerMutex);
    auto found = readers.find(handle);
    if (found != readers.end()) {
        found->second->reader->Release();
        delete found->second;
        readers.erase(found);
    }
}

extern "C" __declspec(dllexport)
int mf_probe(const wchar_t* path, int* width, int* height, int* frames)
{
    MFStartup(MF_VERSION);
    IMFSourceReader* reader = nullptr;
    IMFAttributes* attributes = nullptr;
    MFCreateAttributes(&attributes, 2);
    attributes->SetUINT32(MF_SOURCE_READER_ENABLE_VIDEO_PROCESSING, TRUE);
    HRESULT hr = MFCreateSourceReaderFromURL(path, attributes, &reader);
    attributes->Release();
    if (FAILED(hr) || !reader) {
        MFShutdown();
        return -1;
    }
    IMFMediaType* type = nullptr;
    MFCreateMediaType(&type);
    type->SetGUID(MF_MT_MAJOR_TYPE, MFMediaType_Video);
    type->SetGUID(MF_MT_SUBTYPE, MFVideoFormat_NV12);
    hr = reader->SetCurrentMediaType(MF_SOURCE_READER_FIRST_VIDEO_STREAM,
                                     nullptr, type);
    type->Release();
    if (FAILED(hr)) {
        reader->Release();
        MFShutdown();
        return -2;
    }
    IMFMediaType* current = nullptr;
    reader->GetCurrentMediaType(MF_SOURCE_READER_FIRST_VIDEO_STREAM, &current);
    UINT32 w = 0, h = 0;
    if (current) {
        MFGetAttributeSize(current, MF_MT_FRAME_SIZE, &w, &h);
        current->Release();
    }
    int count = 0;
    while (true) {
        DWORD flags = 0;
        IMFSample* sample = nullptr;
        hr = reader->ReadSample(MF_SOURCE_READER_FIRST_VIDEO_STREAM, 0,
                                nullptr, &flags, nullptr, &sample);
        if (sample) sample->Release();
        if (FAILED(hr) || (flags & MF_SOURCE_READERF_ENDOFSTREAM)) break;
        count++;
    }
    *width = (int)w;
    *height = (int)h;
    *frames = count;
    reader->Release();
    MFShutdown();
    return 0;
}

extern "C" __declspec(dllexport)
int mf_decode_frame(const wchar_t* path, int index, unsigned char* output,
                    int output_size, int* width, int* height, int* stride)
{
    MFStartup(MF_VERSION);
    IMFSourceReader* reader = nullptr;
    IMFAttributes* attributes = nullptr;
    MFCreateAttributes(&attributes, 2);
    attributes->SetUINT32(MF_SOURCE_READER_ENABLE_VIDEO_PROCESSING, TRUE);
    HRESULT hr = MFCreateSourceReaderFromURL(path, attributes, &reader);
    attributes->Release();
    if (FAILED(hr) || !reader) {
        MFShutdown();
        return -1;
    }
    IMFMediaType* type = nullptr;
    MFCreateMediaType(&type);
    type->SetGUID(MF_MT_MAJOR_TYPE, MFMediaType_Video);
    type->SetGUID(MF_MT_SUBTYPE, MFVideoFormat_NV12);
    hr = reader->SetCurrentMediaType(MF_SOURCE_READER_FIRST_VIDEO_STREAM,
                                     nullptr, type);
    type->Release();
    if (FAILED(hr)) {
        reader->Release();
        MFShutdown();
        return -2;
    }
    IMFMediaType* current = nullptr;
    reader->GetCurrentMediaType(MF_SOURCE_READER_FIRST_VIDEO_STREAM, &current);
    UINT32 w = 0, h = 0;
    if (current) {
        MFGetAttributeSize(current, MF_MT_FRAME_SIZE, &w, &h);
        current->Release();
    }
    int copied = -3;
    int current_index = 0;
    while (true) {
        DWORD flags = 0;
        IMFSample* sample = nullptr;
        hr = reader->ReadSample(MF_SOURCE_READER_FIRST_VIDEO_STREAM, 0,
                                nullptr, &flags, nullptr, &sample);
        if (FAILED(hr) || (flags & MF_SOURCE_READERF_ENDOFSTREAM)) {
            if (sample) sample->Release();
            break;
        }
        if (sample) {
            if (current_index == index) {
                IMFMediaBuffer* buffer = nullptr;
                if (SUCCEEDED(sample->ConvertToContiguousBuffer(&buffer)) &&
                    buffer) {
                    BYTE* data = nullptr;
                    DWORD length = 0;
                    if (SUCCEEDED(buffer->Lock(&data, nullptr, &length))) {
                        int pitch = (int)(w * 3 / 2);
                        int needed = pitch * (int)h;
                        if (needed <= output_size) {
                            memcpy(output, data, needed);
                            copied = needed;
                            *stride = pitch;
                        }
                        buffer->Unlock();
                    }
                    buffer->Release();
                }
            }
            sample->Release();
        }
        if (current_index++ >= index) break;
    }
    *width = (int)w;
    *height = (int)h;
    reader->Release();
    MFShutdown();
    return copied;
}


extern "C" __declspec(dllexport)
int mf_audio_decode(const wchar_t* path, int max_seconds,
                    unsigned char* output, int output_size,
                    int* rate, int* channels, int* bits)
{
    MFStartup(MF_VERSION);
    IMFSourceReader* reader = nullptr;
    HRESULT hr = MFCreateSourceReaderFromURL(path, nullptr, &reader);
    if (FAILED(hr) || !reader) { MFShutdown(); return -1; }
    IMFMediaType* type = nullptr;
    hr = reader->GetCurrentMediaType(MF_SOURCE_READER_FIRST_AUDIO_STREAM, &type);
    if (FAILED(hr) || !type) { reader->Release(); MFShutdown(); return -2; }
    type->SetGUID(MF_MT_SUBTYPE, MFAudioFormat_PCM);
    hr = reader->SetCurrentMediaType(MF_SOURCE_READER_FIRST_AUDIO_STREAM,
                                     nullptr, type);
    type->Release();
    if (FAILED(hr)) { reader->Release(); MFShutdown(); return -3; }
    IMFMediaType* current = nullptr;
    reader->GetCurrentMediaType(MF_SOURCE_READER_FIRST_AUDIO_STREAM, &current);
    UINT32 sample_rate = 0, channel_count = 0, bit_count = 0;
    if (current) {
        current->GetUINT32(MF_MT_AUDIO_SAMPLES_PER_SECOND, &sample_rate);
        current->GetUINT32(MF_MT_AUDIO_NUM_CHANNELS, &channel_count);
        current->GetUINT32(MF_MT_AUDIO_BITS_PER_SAMPLE, &bit_count);
        current->Release();
    }
    *rate = (int)sample_rate;
    *channels = (int)channel_count;
    *bits = (int)bit_count;
    int limit = max_seconds > 0 ? max_seconds * sample_rate * channel_count *
                                  (bit_count / 8) : output_size;
    if (limit > output_size) limit = output_size;
    int written = 0;
    while (written < limit) {
        DWORD flags = 0;
        IMFSample* sample = nullptr;
        hr = reader->ReadSample(MF_SOURCE_READER_FIRST_AUDIO_STREAM, 0,
                                nullptr, &flags, nullptr, &sample);
        if (FAILED(hr) || (flags & MF_SOURCE_READERF_ENDOFSTREAM)) {
            if (sample) sample->Release();
            break;
        }
        if (sample) {
            IMFMediaBuffer* buffer = nullptr;
            if (SUCCEEDED(sample->ConvertToContiguousBuffer(&buffer)) && buffer) {
                BYTE* data = nullptr;
                DWORD length = 0;
                if (SUCCEEDED(buffer->Lock(&data, nullptr, &length))) {
                    int copy = (int)length;
                    if (copy > limit - written) copy = limit - written;
                    memcpy(output + written, data, copy);
                    written += copy;
                    buffer->Unlock();
                }
                buffer->Release();
            }
            sample->Release();
        }
    }
    reader->Release();
    MFShutdown();
    return written;
}


extern "C" __declspec(dllexport)
int mf_audio_open(const wchar_t* path, int* rate, int* channels, int* bits)
{
    MFStartup(MF_VERSION);
    IMFSourceReader* reader = nullptr;
    HRESULT hr = MFCreateSourceReaderFromURL(path, nullptr, &reader);
    if (FAILED(hr) || !reader) return -1;
    IMFMediaType* type = nullptr;
    hr = reader->GetCurrentMediaType(MF_SOURCE_READER_FIRST_AUDIO_STREAM, &type);
    if (FAILED(hr) || !type) { reader->Release(); return -2; }
    type->SetGUID(MF_MT_SUBTYPE, MFAudioFormat_PCM);
    hr = reader->SetCurrentMediaType(MF_SOURCE_READER_FIRST_AUDIO_STREAM,
                                     nullptr, type);
    type->Release();
    if (FAILED(hr)) { reader->Release(); return -3; }
    IMFMediaType* current = nullptr;
    reader->GetCurrentMediaType(MF_SOURCE_READER_FIRST_AUDIO_STREAM, &current);
    UINT32 sample_rate = 0, channel_count = 0, bit_count = 0;
    if (current) {
        current->GetUINT32(MF_MT_AUDIO_SAMPLES_PER_SECOND, &sample_rate);
        current->GetUINT32(MF_MT_AUDIO_NUM_CHANNELS, &channel_count);
        current->GetUINT32(MF_MT_AUDIO_BITS_PER_SAMPLE, &bit_count);
        current->Release();
    }
    *rate = (int)sample_rate;
    *channels = (int)channel_count;
    *bits = (int)bit_count;
    std::lock_guard<std::mutex> lock(readerMutex);
    int handle = nextHandle++;
    audioReaders[handle] = new MFReader{reader, (UINT32)channel_count,
                                        (UINT32)bit_count};
    return handle;
}

extern "C" __declspec(dllexport)
int mf_audio_next(int handle, unsigned char* output, int output_size)
{
    std::lock_guard<std::mutex> lock(readerMutex);
    auto found = audioReaders.find(handle);
    if (found == audioReaders.end()) return -1;
    DWORD flags = 0;
    IMFSample* sample = nullptr;
    HRESULT hr = found->second->reader->ReadSample(
        MF_SOURCE_READER_FIRST_AUDIO_STREAM, 0, nullptr, &flags, nullptr,
        &sample);
    if (FAILED(hr) || (flags & MF_SOURCE_READERF_ENDOFSTREAM)) {
        if (sample) sample->Release();
        return 0;
    }
    int copied = 0;
    if (sample) {
        IMFMediaBuffer* buffer = nullptr;
        if (SUCCEEDED(sample->ConvertToContiguousBuffer(&buffer)) && buffer) {
            BYTE* data = nullptr;
            DWORD length = 0;
            if (SUCCEEDED(buffer->Lock(&data, nullptr, &length))) {
                copied = (int)length;
                if (copied > output_size) copied = output_size;
                memcpy(output, data, copied);
                buffer->Unlock();
            }
            buffer->Release();
        }
        sample->Release();
    }
    return copied;
}

extern "C" __declspec(dllexport)
int mf_audio_seek(int handle, double seconds)
{
    std::lock_guard<std::mutex> lock(readerMutex);
    auto found = audioReaders.find(handle);
    if (found == audioReaders.end()) return -1;
    PROPVARIANT position;
    PropVariantInit(&position);
    position.vt = VT_I8;
    position.hVal.QuadPart = (LONGLONG)(seconds * 10000000.0);
    HRESULT hr = found->second->reader->SetCurrentPosition(GUID_NULL, position);
    PropVariantClear(&position);
    return SUCCEEDED(hr) ? 0 : -2;
}

extern "C" __declspec(dllexport)
void mf_audio_close(int handle)
{
    std::lock_guard<std::mutex> lock(readerMutex);
    auto found = audioReaders.find(handle);
    if (found != audioReaders.end()) {
        found->second->reader->Release();
        delete found->second;
        audioReaders.erase(found);
    }
}
