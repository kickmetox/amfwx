#define UNICODE
#define _UNICODE
#include <windows.h>
#include <uiautomationcore.h>
#include <uiautomationcoreapi.h>
#include <oleauto.h>
#include <map>
#include <string>
#include <cstdio>

static const PROPERTYID UIA_NamePropertyId = 30005;
static const PROPERTYID UIA_ControlTypePropertyId = 30003;
static const PROPERTYID UIA_IsEnabledPropertyId = 30010;
static const PROPERTYID UIA_IsOffscreenPropertyId = 30022;
static const PROPERTYID UIA_AutomationIdPropertyId = 30011;
static const PROPERTYID UIA_IsKeyboardFocusablePropertyId = 30009;
static const PROPERTYID UIA_HasKeyboardFocusPropertyId = 30008;
static const PATTERNID UIA_InvokePatternId = 10000;
static const PATTERNID UIA_ValuePatternId = 10002;
static const PATTERNID UIA_TogglePatternId = 10015;
static const int UIA_ButtonControlTypeId = 50000;
static const int UIA_CheckBoxControlTypeId = 50002;
static const int UIA_EditControlTypeId = 50004;
static const int UIA_TextControlTypeId = 50020;
static const int UIA_PaneControlTypeId = 50033;
static const EVENTID UIA_AutomationFocusChangedEventId = 20005;

struct Entry {
    HWND hwnd;
    WNDPROC oldProc;
    int role;
    int controlId;
    std::wstring name;
    RECT bounds;
};

static std::map<HWND, Entry*> entries;

class Provider : public IRawElementProviderSimple,
                 public IRawElementProviderFragment,
                 public IInvokeProvider,
                 public IValueProvider,
                 public IToggleProvider {
public:
    Provider(Entry* entry) : entry_(entry), refs_(1) {}

    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID riid, void** out) override {
        if (!out) return E_INVALIDARG;
        *out = nullptr;
        if (IsEqualIID(riid, IID_IUnknown) ||
            IsEqualIID(riid, IID_IRawElementProviderSimple)) {
            *out = static_cast<IRawElementProviderSimple*>(this);
        } else if (IsEqualIID(riid, IID_IRawElementProviderFragment)) {
            *out = static_cast<IRawElementProviderFragment*>(this);
        } else if (IsEqualIID(riid, IID_IInvokeProvider)) {
            *out = static_cast<IInvokeProvider*>(this);
        } else if (IsEqualIID(riid, IID_IValueProvider)) {
            *out = static_cast<IValueProvider*>(this);
        } else if (IsEqualIID(riid, IID_IToggleProvider)) {
            *out = static_cast<IToggleProvider*>(this);
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
                                                 IUnknown** out) override {
        if (!out) return E_INVALIDARG;
        *out = nullptr;
        if (pattern == UIA_InvokePatternId && entry_->role == 0) {
            *out = static_cast<IInvokeProvider*>(this);
        } else if (pattern == UIA_ValuePatternId && entry_->role == 2) {
            *out = static_cast<IValueProvider*>(this);
        } else if (pattern == UIA_TogglePatternId && entry_->role == 1) {
            *out = static_cast<IToggleProvider*>(this);
        }
        if (*out) AddRef();
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE GetPropertyValue(PROPERTYID property,
                                               VARIANT* value) override {
        if (!value) return E_INVALIDARG;
        VariantInit(value);
        if (property == UIA_NamePropertyId) {
            value->vt = VT_BSTR;
            value->bstrVal = SysAllocString(entry_->name.c_str());
        } else if (property == UIA_ControlTypePropertyId) {
            int types[] = {UIA_ButtonControlTypeId, UIA_CheckBoxControlTypeId,
                           UIA_EditControlTypeId, UIA_TextControlTypeId,
                           UIA_PaneControlTypeId};
            value->vt = VT_I4;
            value->lVal = types[entry_->role >= 0 && entry_->role < 5
                                ? entry_->role : 4];
        } else if (property == UIA_IsEnabledPropertyId) {
            value->vt = VT_BOOL;
            value->boolVal = IsWindowEnabled(entry_->hwnd) ? VARIANT_TRUE
                                                           : VARIANT_FALSE;
        } else if (property == UIA_IsOffscreenPropertyId) {
            value->vt = VT_BOOL;
            value->boolVal = IsWindowVisible(entry_->hwnd) ? VARIANT_FALSE
                                                           : VARIANT_TRUE;
        } else if (property == UIA_IsKeyboardFocusablePropertyId) {
            value->vt = VT_BOOL;
            value->boolVal = VARIANT_TRUE;
        } else if (property == UIA_HasKeyboardFocusPropertyId) {
            value->vt = VT_BOOL;
            value->boolVal = GetFocus() == entry_->hwnd ? VARIANT_TRUE
                                                        : VARIANT_FALSE;
        } else if (property == UIA_AutomationIdPropertyId) {
            wchar_t buffer[32];
            swprintf(buffer, 32, L"amfwx-%d", entry_->controlId);
            value->vt = VT_BSTR;
            value->bstrVal = SysAllocString(buffer);
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
        POINT origin = {entry_->bounds.left, entry_->bounds.top};
        ClientToScreen(GetParent(entry_->hwnd), &origin);
        rect->left = (double)origin.x;
        rect->top = (double)origin.y;
        rect->width = entry_->bounds.right - entry_->bounds.left;
        rect->height = entry_->bounds.bottom - entry_->bounds.top;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE GetEmbeddedFragmentRoots(SAFEARRAY** roots) override {
        if (roots) *roots = nullptr;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE SetFocus() override {
        ::SetFocus(entry_->hwnd);
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE get_FragmentRoot(
        IRawElementProviderFragmentRoot** root) override {
        if (root) *root = nullptr;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE Invoke() override {
        SendMessageW(GetParent(entry_->hwnd), WM_COMMAND,
                     MAKEWPARAM(entry_->controlId, BN_CLICKED),
                     (LPARAM)entry_->hwnd);
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE SetValue(LPCWSTR value) override {
        SetWindowTextW(entry_->hwnd, value ? value : L"");
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE get_Value(BSTR* value) override {
        if (!value) return E_INVALIDARG;
        int length = GetWindowTextLengthW(entry_->hwnd);
        wchar_t* buffer = new wchar_t[length + 1];
        GetWindowTextW(entry_->hwnd, buffer, length + 1);
        *value = SysAllocString(buffer);
        delete[] buffer;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE get_IsReadOnly(BOOL* readonly) override {
        if (!readonly) return E_INVALIDARG;
        *readonly = FALSE;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE get_ToggleState(ToggleState* state) override {
        if (!state) return E_INVALIDARG;
        LRESULT check = SendMessageW(entry_->hwnd, BM_GETCHECK, 0, 0);
        *state = check == BST_CHECKED ? ToggleState_On : ToggleState_Off;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE Toggle() override {
        SendMessageW(entry_->hwnd, BM_CLICK, 0, 0);
        return S_OK;
    }

private:
    Entry* entry_;
    LONG refs_;
};

static LRESULT CALLBACK ProviderProc(HWND hwnd, UINT message,
                                     WPARAM wparam, LPARAM lparam) {
    auto found = entries.find(hwnd);
    if (found == entries.end()) {
        return DefWindowProcW(hwnd, message, wparam, lparam);
    }
    Entry* entry = found->second;
    if (message == WM_GETOBJECT) {
        LONG object_id = (LONG)wparam;
        if (object_id == -1 || object_id == -4 || object_id == 0) {
            return CallWindowProcW(entry->oldProc, hwnd, message, wparam, lparam);
        }
        Provider* provider = new Provider(entry);
        LRESULT result = UiaReturnRawElementProvider(
            hwnd, wparam, lparam,
            static_cast<IRawElementProviderSimple*>(provider));
        provider->Release();
        return result;
    }
    return CallWindowProcW(entry->oldProc, hwnd, message, wparam, lparam);
}

extern "C" __declspec(dllexport)
int amfwx_uia_attach(HWND hwnd, int role, const wchar_t* name, int control_id,
                     int x, int y, int width, int height) {
    if (!hwnd || entries.count(hwnd)) return 0;
    Entry* entry = new Entry{hwnd, nullptr, role, control_id,
                             name ? name : L"", {x, y, x + width, y + height}};
    entry->oldProc = (WNDPROC)SetWindowLongPtrW(hwnd, GWLP_WNDPROC,
                                                (LONG_PTR)ProviderProc);
    entries[hwnd] = entry;
    return 1;
}

extern "C" __declspec(dllexport)
int amfwx_uia_set_bounds(HWND hwnd, int x, int y, int width, int height) {
    auto found = entries.find(hwnd);
    if (found == entries.end()) return 0;
    found->second->bounds = {x, y, x + width, y + height};
    return 1;
}

extern "C" __declspec(dllexport)
int amfwx_uia_set_name(HWND hwnd, const wchar_t* name) {
    auto found = entries.find(hwnd);
    if (found == entries.end()) return 0;
    found->second->name = name ? name : L"";
    return 1;
}

extern "C" __declspec(dllexport)
int amfwx_uia_notify_focus(HWND hwnd) {
    auto found = entries.find(hwnd);
    if (found == entries.end()) return 0;
    Provider* provider = new Provider(found->second);
    HRESULT result = UiaRaiseAutomationEvent(
        static_cast<IRawElementProviderSimple*>(provider),
        UIA_AutomationFocusChangedEventId);
    provider->Release();
    return SUCCEEDED(result) ? 1 : 0;
}

extern "C" __declspec(dllexport)
int amfwx_uia_notify_structure(HWND hwnd) {
    auto found = entries.find(hwnd);
    if (found == entries.end()) return 0;
    Provider* provider = new Provider(found->second);
    HRESULT result = UiaRaiseStructureChangedEvent(
        static_cast<IRawElementProviderSimple*>(provider),
        StructureChangeType_ChildrenInvalidated, nullptr, 0);
    provider->Release();
    return SUCCEEDED(result) ? 1 : 0;
}

extern "C" __declspec(dllexport)
int amfwx_uia_notify_name(HWND hwnd, const wchar_t* old_name,
                          const wchar_t* new_name) {
    auto found = entries.find(hwnd);
    if (found == entries.end()) return 0;
    Provider* provider = new Provider(found->second);
    VARIANT old_value;
    VARIANT new_value;
    VariantInit(&old_value);
    VariantInit(&new_value);
    old_value.vt = VT_BSTR;
    old_value.bstrVal = SysAllocString(old_name ? old_name : L"");
    new_value.vt = VT_BSTR;
    new_value.bstrVal = SysAllocString(new_name ? new_name : L"");
    HRESULT result = UiaRaiseAutomationPropertyChangedEvent(
        static_cast<IRawElementProviderSimple*>(provider),
        UIA_NamePropertyId, old_value, new_value);
    VariantClear(&old_value);
    VariantClear(&new_value);
    provider->Release();
    return SUCCEEDED(result) ? 1 : 0;
}

extern "C" __declspec(dllexport)
int amfwx_uia_detach(HWND hwnd) {
    auto found = entries.find(hwnd);
    if (found == entries.end()) return 0;
    Entry* entry = found->second;
    SetWindowLongPtrW(hwnd, GWLP_WNDPROC, (LONG_PTR)entry->oldProc);
    entries.erase(found);
    delete entry;
    return 1;
}
