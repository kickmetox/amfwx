"""AMFWX - a small self-contained GUI framework."""

from .advanced import (
    Chart, DockManager, DockPane, ImageView, Property, PropertyGrid, Series,
    Splitter, StatusBar, TabView, ToolBar, Tooltip, VideoView,
)
from .canvas import Canvas, Color, Rect
from .clipboard import (
    get_files as get_clipboard_files, get_html as get_clipboard_html,
    get_image as get_clipboard_image, set_image as set_clipboard_image,
    get_text as get_clipboard_text, set_files as set_clipboard_files,
    set_html as set_clipboard_html, set_text as set_clipboard_text,
)
from .dialog import (
    ColorDialog, ColorSwatch, Dialog, FindReplaceDialog, FontDialog, MessageBox,
)
from .dnd import DragEvent, DragManager
from .filedialog import open_file, save_file
from .font import TrueTypeFont
from .jpeg import decode_jpeg
from .render3d import Camera, Mesh, SoftwareRenderer, Texture, clip_near, cube
from .sdl3_backend import Sdl3Error, Sdl3Loop, Sdl3Renderer
from .sdl3 import probe_sdl3
from .touch import GestureEvent, GestureRecognizer, TouchEvent
from .uia import UiaNode, node_from_widget, tree_from_window
from .text import draw_text, measure_text
from .textedit import TextEdit
from .arabic import arabic_shape
from .audio import AudioPlayer, AudioQueuePlayer, Wav, decode_wav
from .settings import Settings, default_path
from .models import ListModel, Model, SortFilterModel, TableModel
from .quick import (ForEach, HStack, ListState, QuickView, Stack, State,
                    Text, TextField, VStack)
from .midi import MidiFile, MidiNote, MidiPlayer
from .resources import ResourcePack
from .crash import CrashLogger
from .security import SecurityError, safe_resource_name, verify_native_dlls
from .ai import (AIError, AIProvider, EchoProvider, OllamaProvider,
                 OpenAICompatibleProvider, provider_from_name)
from .llm_tools import TOOL_SPECS, UiSession, call_tool
from .agent import LLMAgent
from .sdk import SDK, create_sdk
from .conversation import Conversation
from .pdf import canvas_to_pdf
from .db import Database
from .net import HttpClient, NetworkError
from .designer import DesignerCanvas, DesignerDocument, DesignerItem, DesignerWindow
from .studio import Project, ProjectError, Studio, StudioWindow
from .richtext import RichDocument, RichText
from .keystore import KeyStore, KeyStoreError
from .dsp import AudioBuffer, Biquad, DspGraph, Gain, Mixer
from .plugins import Plugin, PluginError, PluginRegistry
from .mixer import MixerPanel, MixerStrip
from .animation import (AnimatedValue, Animation, Timeline, cubic_bezier,
                        ease_in, ease_in_out, ease_out, linear)
from .mfvideo import (MediaAudio, MediaAudioStream, MediaStream, MediaVideo,
                      probe_media_foundation)
from .mediaplayer import MediaPlayer
from .mp4 import Mp4Info, Mp4Track
from .gpu import GPUCompute
from .shaders import compile_dxil
from .shaders import ShaderError, compile_hlsl
from .video import AviVideo, VideoPlayer
from .shader import Shader, ShaderRenderer
from .accessibility import (AccessibilityBridge, AccessibilityNode,
                            AccessibilityTree)
from .uia_native import attach as attach_uia_provider
from .msaa import (Accessible, do_default_action, read_accessible,
                   read_focus, read_location, read_selection,
                   select_accessible, set_accessible_name,
                   set_accessible_value)
from .webp import decode_webp, encode_webp, probe_webp
from .textlayout import Line, TextLayout, bidi_reorder
from .theme import DARK, HIGH_CONTRAST, LIGHT, Theme, get_theme
from .widgets import (
    BoxLayout, Button, CheckBox, ComboBox, FormLayout, GridLayout, Label,
    LineEdit, MenuBar, Panel, ProgressBar, ScrollArea, ScrollBar, Slider,
    TableView,
    TreeItem, TreeView, Widget,
)
from .window import Window

__version__ = "3.13.0"
__all__ = [
    "Canvas", "Color", "Rect", "Window", "Widget", "Panel", "Label",
    "Button", "LineEdit", "CheckBox", "Slider", "ComboBox", "ScrollArea",
    "ProgressBar",
    "ScrollBar", "MenuBar", "TableView", "TreeView", "TreeItem",
    "BoxLayout", "GridLayout",
    "FormLayout", "Dialog", "MessageBox", "FindReplaceDialog", "ColorDialog", "ColorSwatch", "FontDialog", "Settings", "default_path", "Model", "ListModel", "TableModel",
    "SortFilterModel", "QuickView", "State", "ListState", "Stack", "VStack", "HStack",
    "ForEach", "Text", "TextField", "Animation", "Timeline",
    "AnimatedValue", "linear", "ease_in", "ease_out", "ease_in_out",
    "cubic_bezier", "MidiFile", "MidiNote", "MidiPlayer", "ResourcePack", "CrashLogger", "SecurityError", "AIError", "AIProvider", "EchoProvider",
    "OllamaProvider", "OpenAICompatibleProvider", "provider_from_name",
    "TOOL_SPECS", "UiSession", "call_tool", "LLMAgent", "SDK", "create_sdk", "Conversation", "canvas_to_pdf", "Database", "HttpClient", "NetworkError", "DesignerItem", "DesignerDocument",
    "DesignerCanvas", "DesignerWindow", "Project", "ProjectError", "Studio",
    "StudioWindow", "RichDocument", "RichText",
    "KeyStore", "KeyStoreError", "verify_native_dlls",
    "safe_resource_name", "AudioBuffer", "Gain", "Mixer", "Biquad", "DspGraph",
    "Plugin", "PluginError", "PluginRegistry", "MixerPanel", "MixerStrip", "MediaVideo", "MediaStream", "MediaAudio", "MediaAudioStream", "MediaPlayer", "probe_media_foundation", "Mp4Info", "Mp4Track", "GPUCompute", "compile_dxil", "compile_hlsl", "ShaderError", "AviVideo", "VideoPlayer", "Shader", "ShaderRenderer", "AudioPlayer", "AudioQueuePlayer", "Wav", "decode_wav", "Sdl3Renderer", "Sdl3Error", "Sdl3Loop", "Accessible", "AccessibilityNode", "AccessibilityTree", "AccessibilityBridge", "attach_uia_provider", "read_accessible", "do_default_action", "set_accessible_value", "set_accessible_name", "select_accessible", "read_focus", "read_selection", "read_location", "decode_webp", "encode_webp", "probe_webp", "Theme", "DARK", "LIGHT",
    "HIGH_CONTRAST", "get_theme", "draw_text", "measure_text",
    "DragEvent", "DragManager", "TouchEvent", "GestureEvent", "decode_jpeg",
    "TextLayout", "Line", "TextEdit", "get_clipboard_text",
    "set_clipboard_text", "get_clipboard_html", "set_clipboard_html",
    "get_clipboard_files", "set_clipboard_files", "get_clipboard_image",
    "set_clipboard_image", "bidi_reorder", "arabic_shape",
    "GestureRecognizer", "open_file", "save_file", "TrueTypeFont",
    "SoftwareRenderer", "Mesh", "cube", "Camera", "Texture", "clip_near",
    "TabView", "Tooltip", "ImageView", "StatusBar", "ToolBar", "Splitter", "DockManager", "DockPane", "VideoView", "Chart", "Series", "Property", "PropertyGrid",
    "UiaNode", "node_from_widget", "tree_from_window", "probe_sdl3",
]

