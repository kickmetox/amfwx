#define UNICODE
#define _UNICODE
#include <windows.h>
#include <uiautomationcore.h>
#include <uiautomationcoreapi.h>
#include <oleauto.h>
#include <cstdio>

static const PATTERNID UIA_InvokePatternId = 10000;
static const PROPERTYID UIA_NamePropertyId = 30005;
static const PROPERTYID UIA_ControlTypePropertyId = 30003;
static const PROPERTYID UIA_IsEnabledPropertyId = 30010;
static const PROPERTYID UIA_IsOffscreenPropertyId = 30022;
static const int UIA_ButtonControlTypeId = 50000;

static const wchar_t* CLASS_NAME = L"AMFWX.UIAProvider";
static const wchar_t* WINDOW_NAME = L"AMFWX UIA Provider";

class ButtonProvider : public IRawElementProviderSimple,
                       public IInvokeProvider,
                       public IRawElementProviderFragment,
                       public IRawElementProviderFragmentRoot {
public:
    explicit ButtonProvider(HWND hwnd) : hwnd_(hwnd), refs_(1) {}

    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID riid, void** object) override {
        if (!object) return E_INVALIDARG;
        *object = nullptr;
        if (IsEqualIID(riid, IID_IUnknown) ||
            IsEqualIID(riid, IID_IRawElementProviderSimple)) {
            *object = static_cast<IRawElementProviderSimple*>(this);
        } else if (IsEqualIID(riid, IID_IInvokeProvider)) {
            *object = static_cast<IInvokeProvider*>(this);
        } else if (IsEqualIID(riid, IID_IRawElementProviderFragment)) {
            *object = static_cast<IRawElementProviderFragment*>(this);
        } else if (IsEqualIID(riid, IID_IRawElementProviderFragmentRoot)) {
            *object = static_cast<IRawElementProviderFragmentRoot*>(this);
        } else {
            return E_NOINTERFACE;
        }
        AddRef();
        return S_OK;
    }

    ULONG STDMETHODCALLTYPE AddRef() override { return InterlockedIncrement(&refs_); }
    ULONG STDMETHODCALLTYPE Release() override {
        ULONG value = InterlockedDecrement(&refs_);
        if (!value) delete this;
        return value;
    }

    HRESULT STDMETHODCALLTYPE get_ProviderOptions(ProviderOptions* options) override {
        if (!options) return E_INVALIDARG;
        *options = static_cast<ProviderOptions>(
            ProviderOptions_ServerSideProvider | ProviderOptions_UseComThreading);
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE GetPatternProvider(PATTERNID pattern,
                                                 IUnknown** provider) override {
        if (!provider) return E_INVALIDARG;
        *provider = nullptr;
        if (pattern == UIA_InvokePatternId) {
            *provider = static_cast<IInvokeProvider*>(this);
            AddRef();
            return S_OK;
        }
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE GetPropertyValue(PROPERTYID property,
                                               VARIANT* value) override {
        if (!value) return E_INVALIDARG;
        VariantInit(value);
        if (property == UIA_NamePropertyId) {
            value->vt = VT_BSTR;
            value->bstrVal = SysAllocString(WINDOW_NAME);
            return S_OK;
        }
        if (property == UIA_ControlTypePropertyId) {
            value->vt = VT_I4;
            value->lVal = UIA_ButtonControlTypeId;
            return S_OK;
        }
        if (property == UIA_IsEnabledPropertyId) {
            value->vt = VT_BOOL;
            value->boolVal = VARIANT_TRUE;
            return S_OK;
        }
        if (property == UIA_IsOffscreenPropertyId) {
            value->vt = VT_BOOL;
            value->boolVal = VARIANT_FALSE;
            return S_OK;
        }
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE get_HostRawElementProvider(
        IRawElementProviderSimple** host) override {
        if (!host) return E_INVALIDARG;
        *host = nullptr;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE Navigate(NavigateDirection,
                                       IRawElementProviderFragment** result) override {
        if (!result) return E_INVALIDARG;
        *result = nullptr;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE GetRuntimeId(SAFEARRAY** result) override {
        if (result) *result = nullptr;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE get_BoundingRectangle(UiaRect* rect) override {
        if (!rect) return E_INVALIDARG;
        RECT client = {0, 0, 420, 260};
        POINT origin = {0, 0};
        ClientToScreen(hwnd_, &origin);
        rect->left = (double)origin.x;
        rect->top = (double)origin.y;
        rect->width = (double)(client.right - client.left);
        rect->height = (double)(client.bottom - client.top);
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE GetEmbeddedFragmentRoots(SAFEARRAY** roots) override {
        if (roots) *roots = nullptr;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE SetFocus() override {
        ::SetFocus(hwnd_);
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE get_FragmentRoot(
        IRawElementProviderFragmentRoot** root) override {
        if (!root) return E_INVALIDARG;
        *root = this;
        AddRef();
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE ElementProviderFromPoint(double, double,
        IRawElementProviderFragment** result) override {
        if (!result) return E_INVALIDARG;
        *result = nullptr;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE GetFocus(
        IRawElementProviderFragment** result) override {
        if (!result) return E_INVALIDARG;
        *result = nullptr;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE Invoke() override {
        MessageBoxW(hwnd_, L"InvokePattern ausgeloest", L"AMFWX UIA", MB_OK);
        return S_OK;
    }

private:
    HWND hwnd_;
    LONG refs_;
};

static LRESULT CALLBACK WindowProc(HWND hwnd, UINT message,
                                   WPARAM wparam, LPARAM lparam) {
    switch (message) {
    case WM_GETOBJECT: {
        FILE* log = fopen("D:\\AI_Temp\\AMFWX\\native_uia_wm.txt", "a");
        if (log) { fprintf(log, "WM_GETOBJECT %ld\\n", (long)wparam); fclose(log); }
        LONG object_id = static_cast<LONG>(wparam);
        if (true) {
            ButtonProvider* provider = new ButtonProvider(hwnd);
            LRESULT result = UiaReturnRawElementProvider(
                hwnd, wparam, lparam,
                static_cast<IRawElementProviderSimple*>(provider));
            provider->Release();
            return result;
        }
        break;
    }
    case WM_DESTROY:
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProcW(hwnd, message, wparam, lparam);
}

int main() {
    HINSTANCE instance = GetModuleHandleW(nullptr);
    WNDCLASSEXW cls = {};
    cls.cbSize = sizeof(cls);
    cls.lpfnWndProc = WindowProc;
    cls.hInstance = instance;
    cls.lpszClassName = CLASS_NAME;
    RegisterClassExW(&cls);

    HWND hwnd = CreateWindowExW(
        0, CLASS_NAME, WINDOW_NAME, WS_OVERLAPPEDWINDOW,
        100, 100, 420, 260, nullptr, nullptr, instance, nullptr);
    if (!hwnd) {
        printf("CreateWindow failed %lu\n", GetLastError());
        return 1;
    }
    printf("window %p\n", hwnd);
    fflush(stdout);
    ShowWindow(hwnd, SW_SHOW);
    UpdateWindow(hwnd);

    MSG message;
    while (GetMessageW(&message, nullptr, 0, 0) > 0) {
        TranslateMessage(&message);
        DispatchMessageW(&message);
    }
    return 0;
}
