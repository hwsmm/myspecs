
# Chromium Embedded Framework
%ifarch x86_64
%bcond_without cef
%define cef_binary cef_binary_5060_linux64
%else
%bcond_with cef
%endif

%if 0%{?suse_version} > 1500
%define qt_version 6
%else
%define qt_version 5
%endif
%bcond_without websockets

Name:           obs-studio
Version:        29.1.3
Release:        1
Summary:        A recording/broadcasting program
Group:          Productivity/Multimedia/Video/Editors and Convertors
License:        GPL-2.0
URL:            https://obsproject.com/
# we fetch the tarball with a source service, because some subprojects are
# not included in the offical tarball (e.g. obs-browser)
Source:         %{name}-%{version}.tar.xz
%if %{with cef}
BuildRequires:  wget
%endif
Patch0:         0002-Include-diverse-luajit.patch
Patch1:         0001-Prefix-modinfo-with-sbin-since-not-in-normal-path.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  update-desktop-files
BuildRequires:  cmake >= 2.8.12
BuildRequires:  fdk-aac-devel
BuildRequires:  fdupes
BuildRequires:  fontconfig-devel
BuildRequires:  freetype2-devel
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  hicolor-icon-theme
BuildRequires:  libXcomposite-devel
BuildRequires:  libXinerama-devel
BuildRequires:  libXrandr-devel
BuildRequires:  libcurl-devel
BuildRequires:  libjansson-devel
BuildRequires:  pciutils-devel
BuildRequires:  pipewire-devel
BuildRequires:  libpulse-devel
%if "%{qt_version}" == "5"
BuildRequires:  libqt5-qtbase-devel >= 5.3
BuildRequires:  libqt5-qtbase-private-headers-devel
BuildRequires:  libqt5-qtsvg-devel
BuildRequires:  libqt5-qtx11extras-devel >= 5.3
%endif
%if "%{qt_version}" == "6"
BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6Svg)
BuildRequires:  qt6-base-private-devel
%endif
BuildRequires:  libudev-devel
BuildRequires:  libv4l-devel
BuildRequires:  libx264-devel
BuildRequires:  mbedtls-devel
BuildRequires:  pipewire-devel
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(jack)
BuildRequires:  pkgconfig(libavcodec)
BuildRequires:  pkgconfig(libavdevice)
BuildRequires:  pkgconfig(libavfilter)
BuildRequires:  pkgconfig(libavformat)
BuildRequires:  pkgconfig(libavutil)
%ifarch %{ix86} x86_64
BuildRequires:  pkgconfig(libmfx)
%endif
BuildRequires:  pkgconfig(librist)
BuildRequires:  pkgconfig(libswresample)
BuildRequires:  pkgconfig(libswscale)
BuildRequires:  pkgconfig(libva)
BuildRequires:  pkgconfig(lua)
BuildRequires:  pkgconfig(luajit)
BuildRequires:  pkgconfig(srt) >= 1.4
BuildRequires:  pkgconfig(uuid)
%if %{with websockets}
BuildRequires:  pkgconfig(nlohmann_json) >= 3
BuildRequires:  pkgconfig(websocketpp) >= 0.8.0
BuildRequires:  pkgconfig(asio) >= 1.12.1
%endif
BuildRequires:  python3-devel
%if 0%{?suse_version} != 1315 || 0%{?is_opensuse}
BuildRequires:  speexdsp-devel
%endif
BuildRequires:  sndio-devel
BuildRequires:  swig
BuildRequires:  vlc-devel < 20230101.1
%if %{with cef}
BuildRequires:  mozilla-nss
BuildRequires:  mozilla-nspr
%endif
# these deps couldn't be tracked
Requires:       librist4
Requires:       libsrt1_5
Requires:       libspeexdsp1
Recommends:     libqt5-qtwayland
ExclusiveArch:  x86_64 aarch64

# AMF patches
Patch1001:      0001-obs-ffmpeg-Make-AMF-encoder-work-on-Linux.patch
Patch1002:      0002-libobs-opengl-Enable-imported-dmabufs-for-rendering.patch
Patch1003:      0003-libobs-libobs-opengl-enable-gpu-encoding-for-opengl.patch
Patch1004:      0004-libobs-Add-encode_texture2-function-to-struct-obs_en.patch
Patch1005:      0005-obs-ffmpeg-Implement-Linux-AMF-texture-encoding.patch
BuildRequires:  AMF-devel
Requires:       amf-amdgpu-pro

# these are plugins, built as libs and as such should not be mixed up with their originals
%global __provides_exclude_from ^(%{_libdir}/obs-plugins/.*\\.so.*|%{_libdir}/obs-scripting/.*\\.so.*)$
%global __requires_exclude libcef\\.so

%description
Open Broadcaster Software is free and open source software for video recording and live streaming.

%package devel
Summary:        A recording/broadcasting program - Development Files
Group:          Development/Multimedia
Requires:       %{name} = %{version}

%description devel
Open Broadcaster Software is free and open source software for video recording and live streaming.

%prep
%autosetup -p1
%if %{with cef}
wget -O %{_sourcedir}/%{cef_binary}.tar.bz2 https://cdn-fastly.obsproject.com/downloads/%{cef_binary}.tar.bz2
tar xvf %{_sourcedir}/%{cef_binary}.tar.bz2 -C %{_builddir}
%endif

%build
mkdir -p build && cd build
# does not like cmake macro as it fails to link in math.h (-lma
# the compile flags for 15.{4,5} must be relaxed in order to compile obs-studio successfully
cmake \
  -DCMAKE_CXX_STANDARD=17 \
  -DCMAKE_INSTALL_PREFIX=/usr \
%if 0%{?suse_version} == 1500
  -DCMAKE_C_FLAGS:STRING="$CFLAGS %{optflags} -Wno-error=type-limits -Wno-error=unused-variable -Wno-error=deprecated-declarations -Wno-error=return-type -Wno-error=unused-but-set-variable -Wno-error=pointer-sign -Wno-error=reorder" \
  -DCMAKE_CXX_FLAGS:STRING="$CXXFLAGS %{optflags} -Wno-error=type-limits -Wno-error=unused-variable -Wno-error=deprecated-declarations -Wno-error=return-type -Wno-error=unused-but-set-variable -Wno-error=pointer-sign -Wno-error=reorder" \
%endif
  -DUNIX_STRUCTURE=1 \
%if "%{_lib}" == "lib64"
  -DOBS_MULTIARCH_SUFFIX=64 \
%endif
  -DOBS_VERSION_OVERRIDE="$(echo "%{version}" | grep -oE "^[^+]+")" \
  -DENABLE_AJA=OFF \
%if 0%{?sle_version} > 150000 && 0%{?sle_version} < 150500 && 0%{?is_opensuse}
  -DENABLE_PIPEWIRE=OFF \
%endif
  -DENABLE_JACK=ON \
  -DENABLE_LIBFDK=ON \
  -DENABLE_SNDIO=ON \
%if %{with websockets}
  -DENABLE_WEBSOCKET=ON \
%else
  -DENABLE_WEBSOCKET=OFF \
%endif
%if %{with cef}
  -DBUILD_BROWSER=ON \
  -DCEF_ROOT_DIR="%{_builddir}/%{cef_binary}" \
%else
  -DBUILD_BROWSER=OFF \
%endif
  ..

%cmake_build

%install
%cmake_install
%suse_update_desktop_file com.obsproject.Studio
%fdupes %{buildroot}%{_datadir}/obs/

%post
/sbin/ldconfig
%icon_theme_cache_postun

%postun
/sbin/ldconfig
%icon_theme_cache_postun

%files
%{_bindir}/obs
%{_bindir}/obs-ffmpeg-mux
%{_bindir}/obs-amf-test
# Upstream forces libs dir regardless of arch and building plugins is encumbered
# by moving them to the proper directory.
%{_libdir}/obs-plugins/
%{_libdir}/libobs.so.*
%{_libdir}/libobs-frontend-api.so.*
%{_libdir}/libobs-opengl.so.*
%{_libdir}/libobs-scripting.so.*
%{_libdir}/obs-scripting/
%dir %{_datadir}/metainfo
%{_datadir}/metainfo/com.obsproject.Studio.appdata.xml
%{_datadir}/applications/com.obsproject.Studio.desktop
%{_datadir}/icons/hicolor
%{_datadir}/obs

%files devel
%{_libdir}/libobs.so
%{_libdir}/libobs-frontend-api.so
%{_libdir}/libobs-opengl.so
%{_libdir}/libobs-scripting.so
%{_libdir}/cmake
%{_libdir}/pkgconfig/libobs.pc
%{_includedir}/obs

%changelog
* Wed Jun 21 2023 hpj@urpla.net
- Update to version 29.1.3:
  * UI: Translate place holder name for new group
  * UI: Fix changed state of audio settings
  * UI: Fix changing quick transition to/from fade to black
  * UI: Fix checked state of source toolbar menu item
  * text-freetype2: Fix not updating chat log mode property
  * libobs: Update version to 29.1.3
  * obs-ffmpeg: Fix logic in one of the AMF preset fallback checks
  * obs-websocket: Update version to 5.2.3
  * libobs: Set video thread qos class to user interactive on macOS
  * mac-capture: Explicitly set clear background for SCK
  * UI: Don't update text source when nothing changed
  * docs: Clarify da_erase_range
  * deps/obs-scripting: Fix crash removing callbacks in script_unload
  * libobs: Use da_clear() to clear obs_core_data::sources_to_tick
  * libobs/util: Add da_clear()
  * libobs: Don't keep the sources mutex in tick_sources
  * libobs/util: Actually fix use-after-free in da_insert_new
  * libobs/util: Fix use-after-free in darray_insert_new
  * win-capture: Skip compat helper matching if properties are null
  * win-capture: Add Honkai: Star Rail to compatibility list
  * UI: Don't trigger a settings update when list is empty To avoid recursive call
  * obs-ffmpeg: Consider requested throughput in AMF preset fallback
  * obs-ffmpeg: Fix AMF encoder reconfiguration
  * UI: Fix filter shortcuts not showing in context menu
  * text-freetype2: Fix crash after reaching buffer size
  * UI: Fix menu actions missing shortcuts
  * libobs: Fix crash when properties are deleted in callback
  * UI: Assume RTMP if service has no protcol
  * Revert "UI: Reset service selection to custom if name not found"
* Fri Jun  2 2023 Hans-Peter Jansen <hpj@urpla.net>
- libmfx is available for x86 archs only
* Fri Jun  2 2023 Hans-Peter Jansen <hp@urpla.net>
- Build with Qt6 for Tumbleweed and with Qt5 otherwise
* Thu Jun  1 2023 hpj@urpla.net
- Update to version 29.1.2:
  * libobs: Update version to 29.1.2
  * obs-outputs: Remove support for "RTMP Go Away" feature (#8959)
  * UI: Fix crash on patronJsonThread
  * deps/media-playback: Just null the first frame pointer on decode
  * deps/media-playback: Check `is_active` when frame preloading
  * deps/media-playback: Fix crash when interrupting stingers
  * UI: Disallow exiting settings with no track in advanced mode
  * UI: Disallow exiting settings with no track in simple mode
  * UI: Fix crash when receiving multiple SIGINT
  * libobs: Adds obs.hpp to exported header files
  * UI: Only defer property updates for input and transition sources
  * win-dshow: Remove obsolete translation
  * win-capture: Remove obsolete translation
  * obs-qsv11: Add missing translation
  * obs-outputs: Add missing translations
  * obs-filters: Remove obsolete translation in expander-filter
  * obs-filters: Add missing translation in chroma-key-filter
  * obs-ffmpeg: Add missing translations
  * obs-ffmpeg: Add missing translations
  * obs-ffmpeg: Remove obsolete translations
  * mac-videotoolbox: Remove obsolete translation
  * mac-syphon: Remove obsolete translations
  * mac-avcapture: Add missing translation
  * linux-pulseaudio: Add missing translation
  * linux-capture: Remove obsolete translation
  * linux-alsa: Add missing translations
  * UI: Fix missing translations
  * CI: Enable GPU priority setting for Windows builds
  * libobs-d3d11: Set priority to high instead of realtime if HAGS enabled
  * libobs-d3d11: Refactor set_priority to use included header
  * libobs: Remove registry-based HAGS logging
  * libobs-d3d11: Log HAGS status
  * UI: Fix 0,0 size transform bug when resizing sources
  * libobs: Prevent setting invalid scene item scale values
  * libobs: Rework logic for detecting monitoring feedback in PulseAudio
  * libobs: Fix PulseAudio monitoring when device is set to default
  * mac-videotoolbox: Fix incorrect keyframe interval calculation
  * UI: Re-raise missing files dialog on macOS after file is selected
  * UI: Remove tabs for About error statements
  * UI: Process Qt events once after destroy queue finishes
  * UI: Only update vcam output if necessary
  * UI: Reset VCam when clearing scene data
  * deps/obs-scripting: Set file/chunk name when loading lua scripts
  * UI: Fix scene grid mode button color
  * UI: Normalize theme qss files
  * UI: Fix crash when double-clicking projector
  * obs-ffmpeg: Fix compilation when ENABLE_HEVC is not set
  * UI: Reset service selection to custom if name not found
* Tue May 30 2023 Hans-Peter Jansen <hp@urpla.net>
- Relax some compile flags to not error out for Leaps
* Tue May 30 2023 Hans-Peter Jansen <hp@urpla.net>
- Exclude libcef.so dependency tracking correctly
* Wed May 24 2023 hpj@urpla.net
- Update to version 29.1.1:
  * libobs: Update version to 29.1.1
  * UI: Fix crash on macOS when closing OAUTH browser panel
  * UI: Avoid registering CEF OAuth integrations on Wayland
  * obs-websocket: Update submodule to pull translations
  * UI: Exit and show error if clearing scene data fails
  * libobs: Fix luma sampling for packed 4:2:2 sources
  * docs: Add missing elements in Services API
  * UI: Make "Portable Mode" translateable
  * CI: Update ccache cache entries to enable restoration from master branch
  * mac-capture: Fix possible division by zero error
  * UI: Do not show unassigned icon for monitored sources
  * cmake: Enforce -Wmaybe-uninitialized to never turn into an error
  * obs-ffmpeg: Show error if trying to use AV1 fallback
  * UI: Fix FLAC missing from builtin codecs list
  * UI: Relax mc_trans_video_imagescaler.dll DLL block
  * UI: Fix case inconsistency in translation key
  * libobs: Update version to 29.1.0
  * linux-pipewire: Reduce debug message verbosity
  * Update translations from Crowdin
  * obs-qsv11: Set error message for QSV with P216/P416
  * obs-ffmpeg: Set error message for AMF with P216/P416
  * obs-ffmpeg: Set error message for NVENC with P216/P416
  * UI: Fix building macOS/Sparkle without Browser
  * deps/media-playback: Check if frame can be played before using it
  * obs-x264: Disallow 16-bit color formats
  * mac-videotoolbox: Differentiate unsupported format and range errors
  * cmake,UI: Remove unused legacy DSA public key
  * UI: Explicitly focus Ok button in properties dialog
  * cmake: Fix version detection for FFmpeg find module
  * deps/media-playback: Initialize mutex earlier for cached media
  * rtmp-services: Remove defunct servers/services
  * .github: Add workflow to clean caches
  * CI: Switch service checker to macOS
  * obs-filters: Add invert LUT
  * rtmp-services: Fix building with service updates disabled
  * rtmp-services: Enable service updates by default
  * media-playback: Add missing license headers
  * UI: Fix advanced audio encoder bitrate always set to 192
  * rtmp-services: Allow service updates to be disabled on *nix
  * libobs,obs-filters: Align HDR to SDR disparity
  * libobs: Fix mouse button push to talk for linux
  * linux-pipewire: Only consider chunks with size set
  * docs: Remove obs_sceneitem_group_from_scene/source
  * docs: Fix obs_frontend_get_scene_collections() description
  * UI: Fix the license in the AppStream metadata
  * docs: Clarify that data for source/encoder properties can be null
  * libobs: Check for extension validity in os_generate_formatted_filename
  * obs-scripting: Fix loading lua utf8 path
  * rtmp-services: Bump format version to v5
  * UI: Disable auto-remux for AV1+PCM, use MOV for PCM
  * libobs: Finalise source creation before firing signal
  * cmake: Add properties and log viewer UI files to sources list
  * obs-outputs: Don't set DTS offset for enhanced FLV SEQ start/end packets
  * obs-outputs: Fix enhanced RTMP frame type not being set
  * cmake: Set C11 for CMake < 3.21
  * Revert "libobs: Improve util_mul_div64 outside MSVC"
  * libobs: Improve util_mul_div64 outside MSVC
  * mac-virtualcam: Fix DAL plugin entrypoint not being exported
  * UI: Make hotkey edit layout margins symmetrical
  * docs: Add note about instance methods as callbacks in scripting
  * obs-outputs: Log encoder incompatible with dynamic bitrate
  * UI: Sort Add Source menu case insensitively
  * CI: Remove unused pre-cmake 2.0 Info.plist
  * libobs: Remove newly introduced PRAGMA_WARN_STRINGOP_OVERFLOW macro
  * CI: Bump Flatpak actions to v6.1
  * cmake: Fix buildspec version parsing for dependencies
  * UI: Fix simple mode replay buffer maximum not being set
  * UI: Avoid calling libobs functions with null pointers in projectors
  * CI: Update deps to 2023-04-12 release
  * CI: Update apple-actions GitHub Actions
  * UI: Add Citrix ICAService to Windows DLL blocklist
  * UI: Do not disable events when disabling codecs
  * libobs: Add missing headers for framework export
  * cmake: Remove generated libobs export header from install interface
  * CI: Bump Flatpak actions to v6
  * decklink-output-ui: Don't crash on missing device
  * decklink: Ignore "default" output device
  * cmake: Set CFBundleName to "OBS Studio"
  * cmake: Skip plugin target setup when ENABLE_PLUGINS is not set
  * cmake: Skip dependency setup for CEF when using universal architectures
  * cmake: Add platform configuration for macOS universal builds
  * cmake: Fix discovery of existing pre-built dependencies
  * cmake: Set C standard to ISO C17
  * libobs: Fix compiling in ISO C17 mode
  * mac-avcapture: Fix questionable use of comma
  * UI: Replace use of macros for macOS updater with character constants
  * rtmp-services: Remove macro-based constant usage
  * cmake: Fix build without Sparkle
  * cmake: Fix parsing of OBS_VERSION_OVERRIDE cache variable
  * UI: Lower Sparkle update check interval for pre-release builds
  * cmake: Fix parsing BETA version cache variable
  * obs-outputs: Fix AV1 header parser adding ref count to data
  * mac-videotoolbox: Enforce non-zero keyframe interval in CRF mode
  * libobs: Fix transition lookup by uuid
  * UI: Fix incorrect use of QT_TO_UTF8 in SpeakerLayoutChanged
  * UI: Removed unused static AddProjectorMenuMonitors declaration
  * frontend-plugins: Fix auto scene switcher not saving settings on close
  * UI: Recalculate scroll position after resize
  * Revert "UI: Only adjust size of properties on first draw"
  * CI: Enable Sparkle deltas for betas
  * CI: Migrate Steam uploader to macOS
  * libobs: Fix v210 display name
  * libobs: Ensure v210 preserves precision
  * UI: Fix unassigned audio source check in callback
  * obs-ffmpeg: Fix iteration over sample formats
  * obs-ffmpeg: Disable AMF texture encoder runtime reconfiguration
  * UI: Fix simple mode container check
  * UI: Fix "Unqualified call to 'std::move'" warnings
  * UI: Fix replay buffer/split file extension
  * UI: Remove unnecessary variables type conversions
  * mac-videotoolbox: Fix compile issue if HEVC is disabled
  * obs-outputs: Fix HEVC/RTMP composition time missing
  * obs-websocket: Update version to 5.2.2
  * obs-browser: Update version to 2.21.1
  * obs-ffmpeg: Use event for source reconnect thread
  * CI: Fix build errors with Xcode 14.3 and platform SDK 13.3
  * cmake: Remove EXCLUDE_FROM_ALL directive from interface libraries
  * UI: Use name instead of internal extension for incompatible codec check
  * UI: Fix Simple Mode compat check only checking video codec
  * UI: Rework recording format handling
  * obs-qsv11: Log selected codec
  * CI: Specify branches for merge groups
  * obs-ffmpeg: Set framerate for AVCodecContext outputs
  * CI: Update deps to 2023-04-03 release
  * CI: Enable main workflow to run on merge queue items
  * obs-ffmpeg: Allow specifying audio sample format
  * obs-ffmpeg: Compensate for invalid NVENC DTS when using b-frames
  * UI: Don't std::move main in SetUndoProperties
  * UI: Remove unused uppercase format string
  * deps/media-playback: Remove unnecessary log line
  * obs-ffmpeg: Don't use standard newlines in HTML error messages
  * Revert "UI: Fix preview rendering order"
  * UI: Remove UNUSED_PARAMETER where unnecessary
  * decklink: Pass frames between threads using queues
  * UI: Fix rotation handle when source is flipped
  * UI: Use UUIDs for QDataStream
  * UI: Fix preview rendering order
  * UI: Disallow closing settings without selected codec or format
  * Revert "UI: Remove bitness strings"
  * CI: Fix Steam workflow not finding win asset
  * UI: Guard ResetInvalidSelection check behind Qt < 6.5.1
  * UI: Fix replay buffer with fragmented formats
  * obs-ffmpeg: Handle mux errors when writing replay buffer
  * UI: Only use FFmpeg compat check for external codecs
  * cmake: Enable "sortable" flag in UI for large lists
  * cmake: Sort libobs target_sources alphabetically
  * mac-capture: Simplify coreaudio_get_device_id
  * linux-pipewire: Use premultiplied alpha
  * decklink: Avoid swscale for color space
  * decklink: Query for preroll frame count
  * win-dshow: Change buffering for Elgato devices
  * CI: Update deps to 2023-03-30 release
  * obs-ffmpeg: Fix memory corruption during cleanup
  * UI: Add AMD AV1 encoder to simple output mode
  * UI: Update Windows DLL blocklist
  * libobs: Remove dependency on Visual Studio 2019+
  * CI: Update service check PR job to remove set-output
  * CI: Fix GitHub labels check
  * flatpak: Remove jack2 module
  * CI: Remove useless toJSON in Flatpak workflow
  * obs-outputs: Do not strip AV1 padding for RTMP/FLV
  * obs-ffmpeg: Enable padding for NVENC CBR modes
  * UI: Remux fragmented containers to regular counterparts
  * UI: Remux mp4/mov to mp4/mov with suffix
  * UI: Only adjust size of properties on first draw
  * UI: Improve AV1 fallbacks while changing services
  * deps: Fix lower version boundary for file-updater
  * CI: Update macOS packaging to use Xcode archiving and extraction
  * cmake: Add changes required to use Xcode archiving
  * UI: Add exportOptions property lists for Xcode archiving
  * UI: Fix missing masking in unassigned audio mix check
  * win-capture: Fix compat info showing in hotkey mode
  * UI: Fix updater parameters missing a space
  * updater: Add workaround for broken CLI arguments
  * decklink: Schedule video frames for playback
  * CI: Disable Steam nightly upload
  * UI: Add missing compile definitions for service integrations
  * UI: Fix simple stream encoder changed signal-slot connection
  * cmake: Ignore all Qt darwin permission plugins
  * Revert "libobs: Enable fast clear on Windows always"
  * libobs: Log when libobs data file is not found
  * UI: Load service before creating the output handler
  * cmake: Fix obs-frontend-apiConfig.cmake included from 3rd party plugin
  * obs-websocket: Update version to 5.2.1
  * Update translations from Crowdin
  * cmake: Fix OBS_INSTALL_PREFIX
  * libobs/media-io: Use inputs_mutex during close
  * UI/cmake: Fix portable mode (config) not working on Linux
  * obs-websocket: Update version to 5.2.0
  * obs-browser: Update version to 2.21.0
  * enc-amf: Update to 2.8.0
  * CI: Update deps to 2023-03-26 release
  * flatpak: Update deps based on on obs-deps 2023-03-20
  * CI: Only generate and use master branch Flatpak caches
  * obs-outputs: Fix compilation without ENABLE_HEVC
  * CI: Prevent build artifact creation for macOS without pushed tag
  * CI: Update build workflow for macOS
  * CI: Update macOS build scripts to use new CMake presets
  * cmake: Add changes for CMake build framework 3.0
  * cmake: Add Xcode component to CMake build framework 3.0
  * cmake: Add OBS CMake build framework 3.0
  * flatpak: Enable obs-libfdk
  * rtmp-services: Add Joystick.TV
  * rtmp-services: Add IRLToolkit Sydney ingest
  * UI: Rename blending mode "Additive" to "Add" in UI
  * UI: Ignore the leap seconds in tooltip of time format
  * libobs: Add missing VIDEO_FORMAT_V210 handling in switch statements
  * rtmp-services: Add AV1 and HEVC to YouTube RTMPS service
  * rtmp-services: Add AV1 to services schema
  * rtmp-services: Explicitly set codecs for RTMP services
  * obs-outputs: Prevent streaming HDR AV1/HEVC over RTMP
  * libobs,UI: Add output failure code for HDR being unsupported
  * obs-outputs: Add support for AV1/HEVC over RTMP
  * libobs: Export HEVC NAL type enum
  * libobs: Fix VIDEO_FORMAT_V210 shader for GLSL
  * decklink: Add HDR capture support
  * libobs: Add VIDEO_FORMAT_V210
  * UI: Switch RecFormat to RecFormat2
  * deps/media-playback: Fix preloaded videos stopping prematurely
  * UI: Always print debug log to stdout if Debug build
  * UI: Remove unused variable
  * obs-ffmpeg: Use more actionable error messages for hardware encoders
  * CI: Enable PipeWire on Ubuntu 22.04
  * linux-pipewire: Add missing struct typedef for older PipeWire
  * UI: Switch format tooltip based on user selection
  * libobs: Copy private scene item data when duplicating scenes
  * UI: Fix translation key
  * vlc-video: Fix translation key
  * obs-filters: Fix translation key
  * UI: Move tracks in Advanced Standard Recording
  * UI: Enable multiple audio tracks in Simple Output recording
  * UI: Fix transform dialog not being closable
  * UI, libobs: Fix not handled in switch warnings
  * UI: Set fragmented MP4/MOV as default for beta/rc
  * obs-scripting: Enable Python 3.11
  * UI: Properly handle SIGINT on non-Windows platforms
  * UI: Disable incompatible codec/container options
  * UI: Remove ProRes Warning
  * deps/libff: Add ff_format_codec_compatible
  * UI: Add unassigned indicator and warning to mixer
  * UI: Fix issue from stream settings Qt slots refactor
  * libobs: Keep output as premultiplied alpha
  * obs-ffmpeg: Add unclamped 32-bit floating point PCM encoder
  * libobs: Allow encoders to request unclamped audio mix
  * obs-ffmpeg: Add FLAC encoder
  * obs-ffmpeg: Add PCM and ALAC encoders
  * ffmpeg-mux: Properly support lossless codecs
  * UI: Remove outdated NSIS data
  * rtmp-services: Fix supported audio codecs in rtmp_common
  * decklink-output-ui: Align render output paths
  * libobs: Add callback for main texture rendered
  * graphics-hook: Handle VK_KHR_imageless_framebuffer
  * obs-ffmpeg: Add HDR and HEVC to VA-API encoder
  * rtmp-services: Set protocol in rtmp_common if none set
  * UI: Save protocol in non-custom services
  * libobs: Keep mixer data for placeholder sources
  * UI: Make simple audio codec name translatable
  * UI: Fix simple fallback audio codec name
  * UI: Remove unused variables to fix errors in the CMake 3.0 rework
  * UI: Separate translation of filename format tooltip
  * UI: Fix audio archive encoder using the stream track
  * obs-browser: Update version to 2.20.0
  * UI: Add space for right arrow in menu
  * UI: Fix inconsistencies in FindProtocol
  * rtmp-services: Fix formatting and indentation of services schema
  * CI: Avoid installing recommended package on Ubuntu
  * CI: Add nlohmann JSON, WebSocket++ and Asio on Linux
  * cmake: Add finders for Asio and WebSocket++
  * CI: Update deps to 2023-03-20 release
  * image-source: Add slide_changed signal
  * obs-ffmpeg: Pass correct audio codec to muxer subprocess
  * ffmpeg-mux: Set experimental compliance for FFmpeg < 6.0
  * libobs: Enable fast clear on Windows always
  * UI: Enforce stream audio to Opus if service is FTL
  * UI: Default advance record audio to AAC
  * UI: Use connect infos check in before stream check
  * rtmp-services: Add connect infos checks
  * libobs,docs: Add connect infos check to the Services API
  * obs-outputs,obs-ffmpeg: Use connect infos in outputs
  * rtmp-services: Add connect infos to services
  * libobs,docs: Add connect infos to the Services API
  * UI: Add audio codec selections
  * UI: Add Opus bitrate map and per encoder bitrate list
  * obs-ffmpeg: Allow opus for SRT and RIST
  * plugins: Rename audio encoders
  * plugins: Fix codec name on AAC encoders
  * libobs,docs,rtmps-services: Add supported audio codecs
  * UI: Select streaming output based on the protocol
  * rtmp-services: Remove output getter from rtmp_common
  * libobs,docs: Add preferred output type to Service API
  * obs-ffmpeg: Remove AV1 from SRT/RIST supported codecs
  * UI: Remove hardcoded stream codec list
  * UI: Use protocol to enable network options
  * rtmp-services: Remove fallback to H264 if no codec found
  * UI: Use protocol to list compatible codecs
  * UI: Refactor Qt slots in stream settings page
  * libobs,docs: Add supported codecs functions with output id
  * rtmp-services: Add protocol getter to services
  * libobs,docs: Add protocol enumeration functions
  * libobs,docs: Add protocol to Services API
  * rtmp-services: Add protocols to services JSON
  * obs-outputs,obs-ffmpeg: Add protocol to service outputs
  * libobs,docs: Add protocol in Outputs API
  * win-capture: Fix compatibility info showing in any mode
  * libobs: Reduce synchronization limit for multiple audio tracks
  * UI: Fix Dark and System themes select list height
  * docs: Add view functions
  * libobs: Add obs_view_get_video_info
  * UI: Fix media controls shortcuts being global
  * libobs: Fix Pulseaudio audio monitoring listing sources
  * linux-v4l2: Fix fallback framerate for camera
  * obs-outputs: Explicitly close RTMP socket on send error
  * libobs/util: Simplify implementation of os_get_path_extension
  * docs: Clarify a dot is included in the extension
  * test: Add a test for os_get_path_extension
  * test: Fix unused-parameter warnings in test-input
  * libobs: Fix possible use-after-free of obs_scene_t
  * UI: Fix possible use-after-free of obs_scene_t
  * UI: Fix possible use-after-free of obs_source_t
  * UI: Fix macOS crash when saving general settings without Sparkle
  * deps/file-updater: Use LOG_INFO log priority for info logging
  * UI: Properly update filter properties after resetting
  * obs-outputs,UI: Disable Windows-only options on non-Windows
  * UI: Add old Vtuber Maker versions to DLL blocklist
  * UI: Add Help menu action to show What's New dialog
  * UI: Remove Windows 7 browser hwaccel check
  * obs-outputs: Remove Windows 7 sndbuf auto-tuning check
  * obs-ffmpeg: Remove an empty clause
  * aja: Remove an empty clause
  * UI: Remove empty clause
  * flatpak: Add missing CMAKE_BUILD_TYPE
  * obs-ffmpeg: Add GeForce MX450 variant to unsupported NVENC list
  * flatpak: Use Github mirror for nv-codec-headers
  * UI: Fix capitalisation of SysTrayEnabled
  * obs-ffmpeg: Fix translation key capitalisation
  * libobs: Do not send hotkey_bindings_changed if nothing changed
  * libobs: Use uthash for hotkeys and hotkey pairs
  * libobs: Use uthash for properties
  * libobs: Use uthash for hotkey name map
  * libobs: Use uthash for source objects
  * libobs: Use uthash for translation lookup
  * libobs: Use uthash for config
  * libobs: Use uthash for obs data objects
  * libobs/util: Add uthash
  * clang-format: add HASH_ITER to ForEachMacros
  * deps: Add uthash
  * libobs: Add pointer to obs_data_item name
  * linux-pipewire: Report modifiers in hex
  * UI: Refactor integration and browser docks
  * UI: Refactor main docks toggle action
  * UI: Remove platform string from title bar
  * win-capture: Remove the redundant "-" in the CSGO launch option and Steam url language code
  * linux-pipewire: Clear cursor texture on empty bitmap
  * updater: Fix building in Debug
  * Revert "obs-ffmpeg: Use FFmpeg's "fast" AAC encoder by default"
  * UI: Reset UUIDs in duplicated collection
  * libobs: Add obs_reset_source_uuids
  * libobs: Save/Load source UUID in scene item data
  * libobs: Add UUIDs to obs_source objects
  * libobs: Add os_generate_uuid() to platform utils
  * cmake: Add libuuid finder
  * UI: Don't show Update section in settings when built without Sparkle
  * UI: Don't show video-only async filters for synchronous sources
  * UI: Limit preview scrolling
  * UI: Sort and pretty-print exported collections
  * libobs: Add functions for getting/saving pretty JSON
  * UI: Don't try to make OBSBasic parent of ControlsSplitButton
  * UI: Add fragmented MP4/MOV formats
  * UI: Add MP4 to remuxable extensions
  * UI: Create OBSPermissions on stack
  * UI/installer: Add quotes around UninstallString
  * media-playback: Fix libavutil version check
  * UI: Set flathub::manifest
  * UI: Re-raise remux dialog after selecting file on macOS
  * obs-vst: Fix memory leaks on macOS when VST's fail to load
  * UI: Add DLL blocking functionality for Windows
  * mac-virtualcam: Prevent PTS rounding
  * mac-virtualcam: Fix incorrect PTS on Apple Silicon
  * UI: Use bilinear scaling for YT thumbnail
  * UI: Do not set default locale
  * win-capture: Suppress LNK4098
  * UI: Use binary mode for QuickReadFile
  * UI: Add mutex to reading public key file
  * UI,obs-vst: Set Qt RCC format to 1
  * cmake: Set PDBALTPATH manually
  * cmake: Set /Brepro compiler/linker options
  * libobs: Write default values to config
  * obs-outputs: Fix RTMP undefined symbols if built without Mbed TLS
  * CI: Validate compatibility schema
  * win-capture: Display compatibility information
  * updater: Bump version
  * updater: Use native WinHTTP decompression (remove zlib)
  * updater: Use zstd for patch manifest request
  * deps: Remove lzma
  * updater: Switch to Zstandard for delta updates
  * updater: Add Zstandard for compressed downloads
  * obs-ffmpeg,cmake: Add a finder for AMF headers
  * obs-ffmpeg: Replace external/AMF folder by obs-deps headers
  * CI: Create Sparkle appcast and deltas on tag
  * UI: Make T-Bar unclickable
  * mac-syphon: Fix warnings in ObjC code for CMake rework
  * UI: Fix disabled text color in dark theme
  * UI: Set min/max zoom levels for preview
  * UI: Fix wrong program scene if tbar is aborted
  * UI: Fix preview disabled in studio mode
  * libobs: Fix leak with empty path in stats
  * UI: Don't hardcode properties label colors
  * UI: Fix spacing helpers when rotated and flipped
  * CI: Update deps to 2023-03-04 release
  * libobs: Hold async mutex when calling set_async_texture_size
  * obs-ffmpeg: Fix crash during ratecontrol check
  * UI: Add mutex for writing to the log file
  * obs-transitions: Add long description for full decode option
  * libobs: Disable encoder scaling request if it matches output size
  * obs-ffmpeg: Implement QVBR for AMF encoders
  * libobs/media-io: Add color range and space to conversion
  * updater: Check if awaited instance matches current install
  * deps/media-playback: Enable CUDA HW decoder
  * rtmp-services: Add Enchant.events to service list
  * libobs/util: Fix typo in curl revocation support check
  * rtmp-services: Fix whitespace issues in services.json
  * updater: Remove 32-bit Support
  * linux-pipewire: Remove unnecessary variable
  * linux-pipewire: Check for effective crop region
  * linux-pipewire: Adjust cosmetics
  * linux-pipewire: Fix wrong error message
  * linux-pipewire: Demote yet another error to debug
  * rtmp-services: Update Streamvi (#7921)
  * rtmp-services: Update Stripchat streaming service (#8269)
  * rtmp-services: Add LiveStreamerCafe (#8203)
  * rtmp-services: Update Switchboard Live Servers (#8180)
  * rtmp-services: Update Mildom more_info_link (#8334)
  * updater: Multi-threaded delta patching
  * cmake: Enable stricter MSVC compiler options
  * enc-amf: Update submodule
  * win-dshow: Remove obsolete name in REGFILTERPINS
  * obs-ffmpeg: Fix __VA_ARGS__ for comma ellision
  * libobs: Add copy constructor for ComQIPtr
  * UI: Replace uses of token-pasting operator
  * win-capture: Fix possible macro redefinition
  * obs-ffmpeg: Fix for FFmpeg 6 deprecating a flag
  * cmake: Remove FindRSSDK
  * libobs: Fix device functions not marked as EXPORT
  * libobs: Clarify memalign ToDo item
  * UI: Fix tabstops on settings dialog
  * docs: Clarify enum_scenes order
  * docs: Link to obs_scene_from_source in enum_scenes
  * docs: Clarify weak source releasing
  * libobs: Make wcs<->utf8 conversion consistent
  * cmake: Check if Sparkle options are non-empty
  * UI: Remove unused variable
  * obs-ffmpeg: Add full_decode to media source log
  * libobs: Fix scene_audio_render() incorrectly mixing audio
  * obs-transitions: Add option to preload stinger video to RAM
  * CI: Stop pinning Xcode to 14.1
  * UI: Stop virtual camera if active while exiting
  * UI: Fix scene/source in virtual camera config if renamed
  * UI: Refactor Virtual Camera source selector dialog
  * libobs-d3d11: Log D3D11 adapter memory correctly
  * docs: Fix layout and typos
  * UI: Use unordered_map for hotkey duplicate detection
  * UI: Set QT_NO_SUBTRACTOPAQUESIBLINGS env var
  * UI: Defer creation of hotkey dupe icon until needed
  * libobs: Fix pulseaudio monitoring, once and for all
  * UI: Support platform-specific WhatsNew entries
  * linux-pipewire: Read buffer transformation from PipeWire
  * UI: Remove mf_aac references
  * UI: Don't load global plugins in portable mode
  * UI: Only set portable mode variable if supported
  * plugins: Drop win-ivcam
  * plugins: Drop win-mf
  * libobs: Fix non-exhaustive switch statements
  * CI: Remove deprecated dependency installations via Homebrew
  * CI: Remove unit tests from macOS build scripts
  * mac-videotoolbox: Refactor implementation
  * mac-videotoolbox: Add ProRes 4444 (XQ) support
  * libobs,UI: Add P216/P416 pixel formats
  * libobs: Add PQ/HLG support for I210/I412 formats
  * mac-capture: Fix various SCK memory leaks
  * CONTRIBUTING: Add language and PR/Issue template notes
  * CONTRIBUTING: Add AI/Machine Learning policy
  * UI: Disable replay buffer checkbox when using custom FFmpeg
  * UI: Add confirmation dialog for resetting properties
  * UI: Use valueChanged() signal for T-Bar everywhere
  * UI: Fix window text when disabled in dark theme
  * UI: Massive improve hotkey search performance
  * decklink-output-ui: Move preview rescale to GPU
  * decklink: Set video conversion earlier
  * libobs: Add obs_output_get_video_conversion
  * win-capture: Add logging for Force SDR checkbox
  * win-capture: Add Force SDR for DXGI duplicator
  * libobs-d3d11: Support color spaces for duplicator
  * UI: Don't double-delete children of deleted widgets
  * UI: Fix compile error when obs-browser disabled
  * UI: Use native color dialog on macOS
  * UI: Fix button callback in OBSPropertiesView created with an id
  * cmake: Remove ENABLE_SPARKLE_UPDATER option
  * UI: Add update channels (macOS)
  * CI/cmake: Update Sparkle to 2.3.2
  * UI: Merge win-update and nix-update
  * UI: Force Wayland usage on Ubuntu GNOME
  * mac-virtualcam: Fix compiler warnings
  * mac-capture: Fix compiler warnings
  * mac-avcapture: Fix compiler warnings
  * UI: Remove unused variables
  * rtmp-services: Fix missing newline at the end of files
  * obs-x264: Fix non-exhaustive switch statements
  * obs-vst: Fix missing newlines at the end of files
  * obs-transitions: Fix non-exhaustive switch statements
  * obs-filters: Fix non-exhaustive switch statements
  * obs-ffmpeg: Remove unused variables
  * obs-ffmpeg: Fix non-exhaustive switch statements
  * decklink: Add missing newlines at the end of files
  * aja: Remove unused variables
  * libobs-opengl: Refactor macOS implementation
  * libobs-opengl: Fix non-exhaustive switch statement
  * libobs: Remove unused variables
  * libobs: Fix non-exhaustive switch statements
  * media-playback: Fix non-exhaustive switch statement
  * libcaption: Fix missing newline at the end of file
  * UI: Connect Reset button in Transform dialog with main window directly
  * UI: Remove bitness strings
  * UI: Defer Settings window hotkey loading
  * obs-ffmpeg: Relax 'lookahead' constraint when bitrate is updated
  * vlc-video: Fix videos larger than 1080p being squished
  * obs-ffmpeg: Add GeForce MX350 variant to unsupported NVENC list
  * obs-ffmpeg: Handle NV_ENC_ERR_NO_ENCODE_DEVICE error
  * obs-ffmpeg: Restore bad GPU index NVENC error message
  * obs-ffmpeg: NVENC error logging improvements
  * CI: Factorize Github labels checks
  * linux-jack: Prepend devices with "OBS Studio: "
  * UI: Check item whether selected before select To prevent item from being selected again, then mess up the qt internal list order.
  * libobs: Convert security product name to UTF-8 for logging
  * libobs-winrt: Convert errors to UTF-8 with winrt::to_string
  * win-capture: Convert monitor name to UTF-8 for display
  * libobs-d3d11: Convert monitor name to UTF-8 for logging
  * CI: Consistently capitalize PipeWire
  * CI: Add PipeWire package to FreeBSD config for CirrusCI
  * CI: Enable PipeWire on FreeBSD similar to Linux
  * plugins: Enable linux-pipewire on FreeBSD
  * linux-pipewire: Drop unused Linux-only header
  * UI: Refactor / Clean up addNudge
  * UI: Remove unnecessary null checks
  * UI: Fix memory leak of remux window
  * UI: Avoid division by zero when calculating slider position
  * UI: Set remux entry state before adding to queue
  * libobs: Fix typo in function name
  * UI: Improved implementation for sorting filters menu
  * libobs/media-io: Correctly check codec tag compatibility for out stream
  * UI: Correct browse behavior in non-empty input edit line
  * CI,docs: Create separate CF pages artifact
  * CI: Only publish docs on stable tags
  * aja: Add audio channel selection to capture
  * libobs-opengl: Fix projector crash with external macOS displays
  * vlc-video: Support subtitle track up to 1000
  * linux-pipewire: Demote error to debug message
  * obs-ffmpeg: Update AMF SDK to v1.4.29
  * UI: Remove unused Qt crash reporter code
  * linux-pipewire: Trivially shuffle some code around
  * linux-pipewire: Rename obs_pipewire_data to obs_pipewire
  * linux-pipewire: Split initialization of core and streams
  * linux-pipewire: Remove unnecessary struct field
  * linux-pipewire: Inline play_pipewire_stream()
  * linux-pipewire: Move stream properties to constructors
  * linux-pipewire: Cleanup D-Bus proxy on unload
  * linux-pipewire: Return actual type in obs_pipewire_create
  * rtmp-services: Remove defunct servers/services
  * libobs-opengl: Accelerate dmabuf import
  * mac-videotoolbox: Load encoders from system asynchronously
  * UI: Fix scene item edit drag & drop bug
  * win-dshow: Fix virtualcam output a default video format
  * libobs: Add desktop environment to Linux log
  * libobs: Add Flatpak info logging
  * UI: Remove workaround for current scene being deselectable on Qt 6.4.3+
  * UI: Avoid excessive config reads when drawing preview
  * UI: Add check for null widgetForAction result
  * obs-vst: Read plugins in symlink
  * libobs: Avoid position underflow when mixing audio sources
  * obs-filters: Fix preset properties refresh
  * obs-ffmpeg: Fix encoding of 2.1 with FFmpeg aac encoder
  * win-capture: Log display ids
  * libobs-d3d11: Log display ids
  * UI: Fix properties widget being cut off until resize
  * obs-ffmpeg: Initialize SRT stats object before requesting stats
  * flatpak: Override PipeWire to 0.3.65
  * obs-ffmpeg: Remove unused variables
  * libobs/media-io: Add get_total_audio_size()
  * CI: Use cURL for downloading dependency packages
  * UI: Disable properties button in source toolbar
  * graphics-hook: Stop trying to connect early
  * libobs-d3d11: Log display DPI
  * UI: Add obs_frontend_add_undo_redo_action
  * obs-scripting: Add PyType_Modified import for Swig 4.1.1 compat
  * UI: Use input validator on resolution line edit in adv tab
  * UI: Add obs_frontend_open_sceneitem_edit_transform()
  * libobs: Update version to 29.0.2
  * obs-filters: Ensure gain is positive for upward compressor
  * UI: Remove unsupported Windows versions from manifest
  * CI: Publish docs to Cloudflare Pages
  * libobs: Update version to 29.0.1
  * UI: Set macOS appearance on theme change
  * UI: Use native combobox popup on macOS
  * updater: Deduplicate delta patch downloads
  * Revert "UI/updater: Fix files with similar hashes clashing"
  * UI: Hide menu items if source is only audio
  * deps/media-playback: Fix deprecation warning
  * obs-scripting: Fix compilation warnings on Clang and GCC
  * cmake: Allow disabling deprecation errors on GCC/Clang
  * obs-vst: Add reporting of vendor name
  * obs-ffmpeg: Remove unused macro
  * libobs/graphics: Remove unused macros for inputs
  * win-capture: Remove unused macros
  * obs-text: Remove unused macros
  * obs-outputs: Remove unused macro
  * obs-filters: Remove unused macro
  * mac-capture: Remove unused macros
  * docs/sphinx: Add undocumented macros for darray
  * libobs/graphics: Remove unused macros
  * Remove OBSBasicSettings::VideoChangedRestart
  * UI: Remove unused macros
  * UI: Unblock encoder comboboxes signals before change
  * UI: Re-raise properties window after picking files on macOS
  * obs-ffmpeg: Use gai_strerrorA for error logging on Windows
  * obs-filters: Fix wrong number of arguments to error macro
  * virtualcam-module: Update filter size immediately when used in OBS
  * obs-filters: Improve upward compressor with soft knee
  * obs-filters: Make continuous gain on upward compressor
  * obs-filters: Fix expander and upward compressor above threshold
  * linux-pipewire: Reject invalid buffers
  * libobs-opengl: Close display when destroying X11/EGL platform
  * libobs-opengl: Do not close X11 platform display on error
  * libobs: Close display when destroying X11 hotkey platform
  * cmake,obs-ffmpeg: Refactor Libva finder
  * updater: Pass AppData path to elevated process
  * win-capture: Support EnumDisplayDevices failure
  * updater: Add additional status messages
  * libobs: Fix SDR async video on non-SDR targets
  * libobs-d3d11: Log monitor color depth
  * UI: Work around Qt dock restore crash
  * obs-ffmpeg: Tell FFmpeg that BGRA uses alpha
  * frontend-tools: Fix crash on non X11 windowing systems
  * libobs-opengl: Fixup dmabuf queries on X11
  * obs-filters: Improve NVIDIA effects SDK version checks
  * libobs/graphics: Enable DMABUF on FreeBSD and DragonFly
  * UI: Disable screenshot action if item has no video
  * updater: Hash files with multiple threads
  * UI: Don't open properties dialog if item is scene
  * libobs: Fix loading of custom_size for empty scenes
  * CI: Revert Qt to 6.3.1 on Windows
  * cmake: Add workaround for GCC 12.1.0
  * UI: Fix implicit conversion warning on Linux with Clang
  * obs-outputs: Calm some warnings if FTL on Clang and GCC
  * linux-capture: Fix format-overflow warning
  * aja,aja-output-ui: Calm deprecation warnings on Clang and GCC
  * libobs: Calm stringop-overflow warning on GCC
  * libobs,libobs-opengl,obs-ffmpeg-mux: Calm deprecation warnings on *nix
  * cmake: Add workaround for GCC on aarch64
  * cmake: Treat warnings as errors on Clang and GCC
  * obs-filters: Disable RNNoise warning on Clang
  * obslua: Ignore maybe-unitialized warning with SWIG and GCC
  * deps/jansson: Disable warnings on Clang and GCC
  * obs-ffmpeg: Fix compilation warnings on Clang and GCC
  * aja: Fix compilation warnings on Clang and GCC
  * UI: Fix shadow-ivar warning on macOS
  * media-io: Fix FF_API_BUFFER_SIZE_T not being defined on Ubuntu 20.04
  * mac-syphon: Fix unused parameter warning
  * obs-filters: Fix unused parameter warnings
  * obs-scripting: Fix compilation warnings on Clang and GCC
  * plugins: Fix -Wsign-compare on Linux
  * libobs,plugins: Remove individual -Wno-switch
  * libobs: Refactor obs-output encoded use of mixes
  * libobs: Make internal version of remove encoder
  * UI: Remove extra encoder function calls
  * UI: Fix logging of output ID when start fails + code cleanup
  * libobs: Fix logging of remaining views
  * libobs: Prevent encoders from initializing/starting if no media is set
  * libobs: Remove unused internal encoder util function
  * libobs: Allow sending NULL to obs_encoder_set_video/audio()
  * libobs: Protect some encoder functions from being used while active
  * mac-virtualcam: Fix memory access issues for shared IOSurfaces
  * UI: Refactor Windows taskbar switch
  * libobs-d3d11,libobs-opengl,plugins: Remove unneeded cast in switches
  * UI,libobs,libobs-opengl,obs-ffmpeg: Remove unneeded cast in switches
  * libobs: Fix all-except-one switches
  * libobs,plugins: Remove one-case switches
  * libobs: Remove extra space in output reconnect log message
  * docs: Document a few missing obs_output_t function calls
  * libobs: Fix stopping transitions that are not active
  * libobs-winrt,win-capture: Add Force SDR for WGC display
  * win-capture: Show Force SDR setting on Windows 10
  * obs-outputs: Improvements to Windows interface logging
  * libobs-opengl: Drop gl pointers on device_leave_context
  * updater: Fix portable OBS not being relaunched correctly
  * libobs/util: Fix text-lookup not always case-insensitive
  * UI: Reintroduce spacing to YouTube dialog buttons
  * obs-ffmpeg: Remove forced x264 and aac for RTMP
  * rtmp-services: update Mildom servers
- Update to cef_binary_5060_linux64.tar.bz2
- Add new build dependencies: asio, nlohmann_json, websocketpp and
  uuid
- Remove 8376.patch
* Thu May 18 2023 Marcus Rueckert <mrueckert@suse.de>
- packaging fixes
  - Build with Qt6 (can be switched with the qt_version define on
    top)
  - update buildrequires for the websocket support
  - pkgconfig(asio)
  - pkgconfig(websocketpp)
  - pkgconfig(nlohmann_json)
  - enable sndio support (new BR: sndio-devel)
  - pkgconfig(uuid) is now required
  - enable libfdk support to fix AAC support
* Fri May 12 2023 Hans-Peter Jansen <hp@urpla.net>
- Apply upstream pull request 8376.patch to fix build with ffmpeg >= 6
* Sat Apr 22 2023 Hans-Peter Jansen <hpj@urpla.net>
- Disable __requires_exclude_from for testing
* Tue Apr 18 2023 Hans-Peter Jansen <hp@urpla.net>
- Add more hidden deps
* Sat Feb  4 2023 hpj@urpla.net
- Update to version 29.0.2:
  * libobs: Update version to 29.0.2
  * obs-filters: Ensure gain is positive for upward compressor
  * CI: Publish docs to Cloudflare Pages
  * libobs: Update version to 29.0.1
  * UI: Unblock encoder comboboxes signals before change
  * UI: Re-raise properties window after picking files on macOS
  * obs-ffmpeg: Use gai_strerrorA for error logging on Windows
  * obs-filters: Fix wrong number of arguments to error macro
  * virtualcam-module: Update filter size immediately when used in OBS
  * obs-filters: Improve upward compressor with soft knee
  * obs-filters: Make continuous gain on upward compressor
  * obs-filters: Fix expander and upward compressor above threshold
  * libobs-opengl: Close display when destroying X11/EGL platform
  * libobs-opengl: Do not close X11 platform display on error
  * libobs: Close display when destroying X11 hotkey platform
  * cmake,obs-ffmpeg: Refactor Libva finder
  * updater: Pass AppData path to elevated process
  * win-capture: Support EnumDisplayDevices failure
  * updater: Add additional status messages
  * libobs: Fix SDR async video on non-SDR targets
  * libobs-d3d11: Log monitor color depth
  * UI: Work around Qt dock restore crash
  * obs-ffmpeg: Tell FFmpeg that BGRA uses alpha
  * frontend-tools: Fix crash on non X11 windowing systems
  * libobs-opengl: Fixup dmabuf queries on X11
  * obs-filters: Improve NVIDIA effects SDK version checks
  * libobs/graphics: Enable DMABUF on FreeBSD and DragonFly
  * libobs: Fix loading of custom_size for empty scenes
  * CI: Revert Qt to 6.3.1 on Windows
  * UI: Remove extra encoder function calls
  * UI: Fix logging of output ID when start fails + code cleanup
  * libobs: Fix logging of remaining views
  * libobs: Prevent encoders from initializing/starting if no media is set
  * libobs: Remove unused internal encoder util function
  * libobs: Allow sending NULL to obs_encoder_set_video/audio()
  * libobs: Protect some encoder functions from being used while active
  * mac-virtualcam: Fix memory access issues for shared IOSurfaces
  * libobs: Remove extra space in output reconnect log message
  * docs: Document a few missing obs_output_t function calls
  * libobs: Fix stopping transitions that are not active
  * win-capture: Show Force SDR setting on Windows 10
  * libobs-opengl: Drop gl pointers on device_leave_context
  * updater: Fix portable OBS not being relaunched correctly
  * libobs/util: Fix text-lookup not always case-insensitive
  * UI: Reintroduce spacing to YouTube dialog buttons
  * obs-ffmpeg: Remove forced x264 and aac for RTMP
  * rtmp-services: update Mildom servers
  * updater: Deduplicate Downloads
  * obs-filters: disable NVIDIA FX audio model loading when SDK is not installed
  * Update translations from Crowdin
  * UI: Prevent negative "disk full in" calculation when no output
  * linux-pipewire: Check format availablity against DRM only for dmabufs
  * UI: Disable qt5ct when compiled with qt6
  * docs: Clarify enum functions return value
  * docs: Add script_description to scripting
* Thu Jan 19 2023 Hans-Peter Jansen <hp@urpla.net>
- Add an additional runtime dependency: librst1_5
* Sun Jan  8 2023 hpj@urpla.net
- Update to version 29.0.0:
  * rtmp-services: Specify RTMP_SERVICES_FORMAT_VERSION in package.json
  * CI: Revise repository conditions to validate JSON schema of services
  * libobs: Update version to 29.0.0
  * win-capture: Always reset timeout when searching for target display
  * UI: Lock volume meter sliders to LTR
  * UI: Use stream encoder when resetting encoders
  * obs-filters: Log NVIDIA Effects version only if lib is found
  * CI: Use Flatpak build-bundle option
  * CI: Update Flatpak Actions
  * Revert "libobs-d3d11: Default to Intel IGPU on IGPU+DGPU systems"
  * Revert "libobs-d3d11: Make sure libobs knows the new adapter index"
  * Revert "libobs: Fix adapter index not getting applied to resets"
  * UI: Restrict GNOME wayland override
  * obs-ffmpeg, obs-qsv11: Ensure adapter order in encoder tests
  * obs-ffmpeg: Remove EnumOutputs from encoder tests
  * libobs: Add funcs to get windows video adapter LUIDs
  * rtmp-services: Remove defunct servers/services
  * obs-ffmpeg: Set chroma location for VA-API
  * obs-qsv11: Put mastering primaries in GBR order
  * mac-videotoolbox: Add HDR metadata
  * obs-ffmpeg: Fix AMF default CQP value
  * libobs: Duplicate URL string for OBS_BUTTON_URL
  * UI: Fix Qt AutoUic warning
  * obs-ffmpeg: Add new rate control method mappings for AVC/HEVC
  * obs-filter: Fix upward compressor
  * obs-ffmpeg: Use enum for av1 encoders
  * cmake: Fix FindGio.cmake to find libgio
  * docs: Add missing source functions
  * obs-ffmpeg: Bump AMF version to v1.4.29
  * obs-ffmpeg: Add new rate control methods for AMD AVC/HEVC
  * docs: Fix reference count info of obs_frontend_get_streaming_service
  * libcaption: Fix invalid data at utf8_load_text_file
  * docs: Add versionadded for 29.0.0 functions
  * docs: Add info on property modified callback
  * mac-videotoolbox: Don't parse HEVC as AVC
  * UI: Guard GetMonitorName behind Qt < 6.4
  * UI: Fix slide counter with no slides
  * obs-ffmpeg: Improve chroma location decision
  * docs: Clarify signal_handler_connect()
  * obs-filters: Use correct signal to reset greenscreen filter
  * image-source: Remove cleared missing files from slideshow
  * libobs: Override fps ovi for aux views
  * updater: Bump to version 2.2
  * obs-ffmpeg: Allow srt stream to disconnect after timeout
  * rtmp-services: Add Bitmovin
  * obs-qsv11: Set subprocess timeout to 10 sec
  * win-dshow: Ignore FFmpeg colorspace if overridden
  * obs-ffmpeg: Disable VBAQ for H264 CQP rate control
  * obs-qsv11: Fix QSV detection
  * obs-qsv11: Fix encoder capping resolution on dgpus
  * Revert "obs-qsv11: Don't set to low power mode if AV1"
  * obs-qsv11: Fix HDR not working with AV1
  * obs-qsv11: Don't set to low power mode if AV1
  * obs-qsv11: Keep ExtParam value around
  * UI: Hide "Update Channel" label on macOS
  * UI: Guard AutoBetaOptIn as Windows-only
  * UI: Delay timed update check until branch migration
  * UI: Fix monitor name for projectors on Windows
  * obs-qsv11: Remove statics, fix buffer misuse
  * obs-qsv11: Add HEVC
  * obs-qsv11: Don't declare vars in switch w/o braces
  * obs-qsv11: Remove unused function
  * obs-qsv11: Fix profile default for AV1
  * obs-qsv11: Remove unused function declaration
  * obs-ffmpeg: Disable VBAQ for HEVC CQP rate control
  * libobs: Suppress LNK4098
  * rtmp-services: Suppress LNK4098
  * UI: Add QSV AV1 to simple output mode
  * obs-qsv11: Simplify CQP
  * obs-qsv11: Add QSV AV1 encoder
  * obs-qsv11: Add codec enum
  * obs-qsv11: Only reinitialize bitrate
  * obs-qsv11: Add startup process to test QSV support
  * libobs: Fix adapter index not getting applied to resets
  * UI: Switch to beta branch when running beta/rc for the first time
  * UI: Add update channels (Windows)
  * updater: Add --branch/--portable command line arguments
  * cmake/libobs: Set OBS_COMMIT based on git describe
  * flatpak: Update deps based on obs-deps 2022-11-21
  * CI: Update deps to obs-deps 2022-11-21 release
  * libobs-d3d11: Make sure libobs knows the new adapter index
  * obs-ffmpeg: Fix building without HEVC on Windows
  * cmake: Specify utf-8 for MSVC builds
  * CI,obs-vst: Update Flatpak KDE Runtime to version 6.4
  * UI, image-source: Add slide counter to slideshow toolbar
  * obs-vst: Improve some string handling
  * obs-vst: Use libobs memory allocation functions
  * UI: Disable toolbar buttons when no source is selected
  * obs-ffmpeg: Improve RIST/SRT log messages
  * UI: Use blog for "Attempted path" log messages
  * ffmpeg: fix cqp rate control on svtav1
  * ffmpeg: fix "cqp" mode for libaom
  * libobs: Deprecate obs_get/set_master_volume
  * obs-browser: Don't use QPointF for pointer position
  * obs-browser: Update version to 2.19.0
  * libdshowcapture: Support more capture cards with uncoupled audio
  * obs-ffmpeg: Use Libva in FFmpeg VA-API
  * UI: Add filters button to scenes toolbar
  * UI: Remove Qt taskbar overlay
  * obs-ffmpeg: Fix SVT-AV1 rate control mode selection
  * libobs: Allow overriding video resolution per view
  * decklink: Always output BGRA
  * UI: Clarify that RGB output format is BGRA
  * flatpak: Add Jansson to modules
  * mac-videotoolbox: Default to High profile
  * UI: Add Apple Hardware Encoder to AutoConfig
  * win-dshow: Recognise higher FPS values from devices
  * CI: Name Docs zip based on commit/tag
  * obs-ffmpeg: Fix encoder preset quality fallbacks for AVC/HEVC/AV1
  * obs-ffmpeg: Suggest docs to reference for AMF/FFmpeg options
  * UI: Add AMD AV1 to simple output mode
  * obs-ffmpeg: Add AMF AV1 encoder
  * obs-ffmpeg: Use codec enum for AMF texture encode check
  * obs-ffmpeg: Make AMF AVC encoder name consistent w/ others
  * obs-ffmpeg: Only show b-frames AMF property for AVC
  * obs-ffmpeg: Only allow AMF high/baseline profiles for AVC
  * obs-ffmpeg: Allow 0-51 for CQP property
  * obs-ffmpeg: Use codec enum for amf_properties_internal
  * obs-ffmpeg: Fix transcoding API typo
  * obs-ffmpeg: Update AMF SDK for AV1 support
  * UI: Change Simple Output NVENC default preset to P5
  * CI: Re-enable scripting in Windows builds
  * obs-ffmpeg: Change default nvenc preset to P5
  * win-capture,UI: Look up display by id, not index
  * Revert "virtualcam-module: Don't send frames on initial pause"
  * obs-websocket: Update version to 5.1.0
  * obs-ffmpeg: Fix SRT error type comparison (#7802)
  * win-capture: Invert output when drawing monochrome cursors
  * rtmp-services: Add ffmpeg-mpegts-muxer in schema v4
  * obs-ffmpeg: Direct setting of  encryption & auth for SRT & RIST
  * UI: Use weak source for projectors
  * obs-ffmpeg: Use compatibility options on nvnenc init fail
  * libobs: Fix SRGB to SCRGB async video rendering
  * CI: Fix building in PowerShell 7.3.x
  * CI: Fix services checkers using wrong port for RTMPS
  * UI: Add separator in source toolbar
  * obs-outputs: Shorten dynamic bitrate increment timeout
  * rtmp-services: Add IRLToolkit
  * UI: Remove number from multiview labels
  * CI: Add debian debug symbols to CI artifacts
  * cmake: Fix debian packages loosing all debug symbols
  * mac-capture: Disable all SCK modes besides WindowCapture on macOS 12
  * mac-videotoolbox: Support P010 and HDR color spaces
  * obs-filters: NVIDIA Background Removal variable mask refresh
  * obs-filters: Add temporal processing to Background Removal
  * obs-filters: Warn if NVIDIA Audio FX is outdated
  * obs-filters: Warn if NVIDIA Video FX is oudated
  * obs-outputs: Increase librtmp send timeout to 15 seconds
  * UI: Fix snprintf calls with literals as buffer sizes
  * obs-outputs: Fix snprintf calls with literals as buffer sizes
  * obs-filters: Fix snprintf calls with literals as buffer sizes
  * image-source: Fix snprintf calls with literals as buffer sizes
  * coreaudio-encoder: Fix snprintf calls with literals as buffer sizes
  * obs-x264: Fix snprintf calls with literals as buffer sizes
  * win-capture: Replace invocations of sprintf with snprintf
  * obs-ffmpeg: Replace invocations of sprintf with snprintf
  * libobs-d3d11: Replace invocations of sprintf with snprintf
  * linux-v4l2: Replace invocations of sprintf with snprintf
  * linux-capture: Replace invocations of sprintf with snprintf
  * UI: Replace invocations of sprintf with snprintf
  * obs-outputs: Replace invocations of sprintf with snprintf
  * mac-capture: Replace invocations of sprintf with snprintf
  * libobs: Replace invocations of sprintf with snprintf
  * deps: Replace invocations of sprintf with snprintf
  * obs-ffmpeg: Fix deprecation of channels member of several structs
  * libobs: Change audio resampler to new channel API
  * obs-ffmpeg: Update mpegts to channel API change
  * docs: Add info on funcs to use for properties
  * aja: Fix capturing UHD/4K YUV on Kona HDMI.
  * UI: Fix QStyle memory leak
  * libobs-d3d11: Support advanced SDR window preview
  * mac-capture: Support P3 for HDR recordings
  * libobs: Add P3 shaders for Mac
  * libobs-opengl: Support l10r IOSurface
  * decklink-output-ui: Pipeline GPU data for preview
  * libobs: Log Windows emulation status
  * libobs: Log macOS Rosetta status
  * UI: Remove Rosetta detection log
  * libobs/util: Add function to get Windows x64 emulation status
  * UI: Use on_foo_bar properly for docks context menu
  * UI: Replace manual usage of on_foo_bar for show/hide transition
  * UI: Remove support for toggling Aero
  * libobs: Remove Aero logging
  * mac-avcapture: Add DeskCam support
  * rtmp-services: Add Whowatch
  * libobs: Fix reading Windows release name
  * UI: Set Replay Buffer Memory limit dynamically
  * libobs: Add utility function to get total RAM
  * libobs: Move async filtering from render to tick
  * libobs: Add "source_update" signal
  * docs: Add clarifications
  * UI: Fix always on top not being saved on exit
  * libobs: Update to 28.1.2
  * CI: Upload beta builds as Steam Playtest
  * obs-filters: Add a simple 3-band equalizer
  * obs-browser: Update version to 2.18.7
  * UI: Add simple mode for Apple Hardware HEVC
  * UI: Add detection of ProRes encoder for auto muxing
  * UI: Print container warnings for ProRes encoder and disable autoremux
  * libobs: Force hvc1 codec tag for HEVC video and respect input tags
  * mac-videtoolbox: Use correct size for system representation CFStrings
  * mac-videotoolbox: Make unsupported color format text codec agnostic
  * mac-videotoolbox: Remove HW_ACCEL flags
  * mac-videotoolbox: Add support platform hardware and software ProRes 422
  * obs-ffmpeg: Add codec-tag support to ffmpeg-mux
  * mac-videotoolbox: Add support for platform hardware and software HEVC
  * Revert "obs-ffmpeg: Check nvenc max bframe count"
  * obs-ffmpeg: Cap NVENC Max B-frames according to GPU caps
  * CI: Fix service validator
  * libobs: Update version to 28.1.1
  * obs-ffmpeg: Check nvenc max bframe count
  * UI: Migrate Simple Output NVENC preset
  * UI: Refactor NVENC preset migration
  * libobs: Update version to 28.1.0
  * libobs: Force SRGB conversion for tonemapped video
  * obs-ffmpeg: Split NVENC preset migrations by codec
  * UI: Add NVENC preset migration for lossless
  * obs-ffmpeg: Align NVENC preset migrations to NVIDIA guidelines
  * obs-ffmpeg: Add NVENC preset mapping for old Default preset
  * obs-ffmpeg: Swap hq and mq preset order
  * UI: Change adv audio background color
  * UI/obs-frontend-api: Return allocated strings for new funcs
  * obs-frontend-api: Add functions to get last saved files
  * libobs: Fix blend method in studio mode
  * libobs: Add media key support for linux
  * win-capture: Disable clang-format for assembly patterns
  * obs-filters: Fix typo in Upward.Compressor
  * obs-ffmpeg: Fix Ubuntu 20.04 detection
  * obs-ffmpeg: Fix FFmpeg NVENC presets on Ubuntu 20.04
  * obs-filters: Fix comment typo
  * obs-filters: Add upward compressor filter
  * obs-filters: Refactor expander filter expansion code
  * obs-filters: Use snake_case for expander variables
  * Update translations from Crowdin
  * obs-browser: Update version to 2.18.6
  * enc-amf: Minor compilation improvements
  * UI: Use correct key for "Always on Top" with projectors
  * rtmp-services: Add Vindral service
  * UI: Fix placeholder element not being deleted
  * UI: Avoid showing service integration page on Wayland
  * obs-frontend-api: Add screenshot event
  * UI: Set preset2 instead preset for simple mode NVENC
  * UI: Hide --portable from help text if disallowed
  * UI: Hide donation CTA when running via Steam
  * UI: Add --steam flag
  * linux-v4l2: Send STREAMON/STREAMOFF on vcam start/stop
  * docs: Fix sphinx import error on Python 3.10+
  * obs-ffmpeg: Fix NVENC "mq" to use P6 rather than P4
  * UI: Change "hq" to use P5 when upgrading NVENC
  * UI: Fix stats widget appearance on Yami themes
  * UI: Fix stats widget status font size
  * UI: Fix theme if apply and cancel in settings
  * CI: Fix Steam launching x86 version under Rosetta
  * mac-virtualcam: Remove unnecessary IOSurfaceLocks in Mach Server
  * mac-virtualcam: Remove unnecessary use of NSAppleEventDescriptor
  * mac-virtualcam: Use IOSurfaceLock on Intel-based Macs only
  * mac-virtualcam: Fix random crashes in applications loading VirtualCam
  * CI: Fix services check using deprecated GHA output
  * CI: Update GitHub Actions for set-output deprecation
  * UI: Use correct title for failed replay buffer start
  * obs-frontend-api: Add theme functions
- Add new required pkgconfig(libva) build dependency
- Refine srt build dependency (>= 1.4)
* Tue Dec  6 2022 Hans-Peter Jansen <hp@urpla.net>
- Explicitly require librist4 (dlopen'ed)
* Mon Nov 14 2022 Hans-Peter Jansen <hpj@urpla.net>
- Exclude any requires from %%{_libs}/{obs-plugins,obs-scripting}
  libraries as well
* Fri Nov 11 2022 hpj@urpla.net
- Update to version 28.1.2:
  * UI: Fix always on top not being saved on exit
  * libobs: Update to 28.1.2
  * obs-browser: Update version to 2.18.7
* Wed Nov  9 2022 Hans-Peter Jansen <hpj@urpla.net>
- Exclude any auto provides from %%{_libs}/{obs-plugins,obs-scripting}
  libraries
* Thu Nov  3 2022 hpj@urpla.net
- Update to version 28.1.1:
  * Revert "obs-ffmpeg: Check nvenc max bframe count"
  * obs-ffmpeg: Cap NVENC Max B-frames according to GPU caps
  * CI: Fix service validator
  * obs-ffmpeg: Check nvenc max bframe count
  * libobs: Update version to 28.1.1
  * UI: Migrate Simple Output NVENC preset
  * UI: Refactor NVENC preset migration
  * libobs: Update version to 28.1.0
  * libobs: Force SRGB conversion for tonemapped video
  * obs-ffmpeg: Split NVENC preset migrations by codec
  * UI: Add NVENC preset migration for lossless
  * obs-ffmpeg: Align NVENC preset migrations to NVIDIA guidelines
  * obs-ffmpeg: Add NVENC preset mapping for old Default preset
  * obs-ffmpeg: Swap hq and mq preset order
  * libobs: Fix blend method in studio mode
  * obs-ffmpeg: Fix Ubuntu 20.04 detection
  * obs-ffmpeg: Fix FFmpeg NVENC presets on Ubuntu 20.04
  * Update translations from Crowdin
  * obs-browser: Update version to 2.18.6
  * enc-amf: Minor compilation improvements
  * UI: Use correct key for "Always on Top" with projectors
  * rtmp-services: Add Vindral service
  * UI: Fix placeholder element not being deleted
  * UI: Avoid showing service integration page on Wayland
  * UI: Set preset2 instead preset for simple mode NVENC
  * UI: Hide --portable from help text if disallowed
  * UI: Hide donation CTA when running via Steam
  * UI: Add --steam flag
  * linux-v4l2: Send STREAMON/STREAMOFF on vcam start/stop
  * docs: Fix sphinx import error on Python 3.10+
  * obs-ffmpeg: Fix NVENC "mq" to use P6 rather than P4
  * UI: Change "hq" to use P5 when upgrading NVENC
  * UI: Fix stats widget appearance on Yami themes
  * UI: Fix stats widget status font size
  * UI: Fix theme if apply and cancel in settings
  * CI: Fix Steam launching x86 version under Rosetta
  * mac-virtualcam: Fix random crashes in applications loading VirtualCam
  * CI: Fix services check using deprecated GHA output
  * CI: Update GitHub Actions for set-output deprecation
  * UI: Use correct title for failed replay buffer start
  * obs-filters: Remove unused assignments
  * UI: Check return value of ConvertResText before accessing results
  * libobs: Add ifdef for Windows-only variable assignment
  * UI: Fix potential memory leak when parsing OBSThemeMeta
  * UI: Copy result of getenv before use
  * UI: Remove unused assignments
  * UI: Fix possible crash due to UI property access from graphics thread
  * virtualcam-module: Fix crash on resolution change
  * virtualcam-module: Clarify resolution variables
  * obs-ffmpeg: Clarify name of NVENC preset
  * virtualcam-module: Don't send frames on initial pause
  * UI: Don't offer current resolution in auto config if < 240p
  * UI: Swap mq and hq NVENC Preset mappings
  * Revert "libobs: Update version to 28.1.0"
  * libobs: Update version to 28.1.0
  * UI: Use transform to fit vcam source to canvas
  * Revert "UI: Remove individual sources (for now) from vcam config"
  * docs: Add obs_sceneitem_group_enum_items API call to scripting docs
  * obs-scripting: Add obs_sceneitem_group_enum_items function call
  * mac-capture: Log CoreAudio device sample rate
  * obs-scripting: Fix block comment formatting
  * obs-scripting: Fix script state variable being reset by tick callback
  * mac-videotoolbox: Remove "None" profile
  * rtmp-services: Remove defunct servers/services
  * UI: Move "Always On Top" into View menu
  * UI: Add multiview menus to UI file
  * vlc-video: Fix crash at removing files from missing-file dialog
  * rtmp-services: Update ingest list for Restream.io
  * obs-vst: Toggle properties button visibility upon VST selection
  * linux-pulseaudio: Use DONT_MOVE for non-default devices
  * UI: Fix NVENC AV1 preset while resetting encoders
  * win-capture: Update D3D9 signature for Win 11 22H2
  * UI: Clamp float values possibly representing infinity to integer size
  * win-capture: Fix reporting valid width and height if not capturing
  * libobs: Sample video at default chroma location
  * rtmp-services: Update Glimesh to add RTMP ingests
  * UI: Add NVENC AV1 to simple output mode
  * obs-ffmpeg: Add NVENC AV1 support
  * libobs/graphics: Precompute more accurate matrix
  * libobs: Precompute more accurate matrices
  * libobs: Update version to 28.0.3
  * UI: Fix alignment of volume sliders
  * mac-videotoolbox: Remove unused defines
  * UI: Fix tabstop on settings dialog
  * UI: Remove unnecessary styles
  * obs-scripting: Enable Python autodoc
  * obs-scripting: Re-enable Python annotations
  * docs: Add links to python functions
  * CI: fix build on non-x86 Linux platforms
  * win-wasapi: Fix Stop hang
  * UI: Fix AutoRemux not working when FFmpeg output configured
  * win-wasapi: Don't reconnect when inactive
  * obs-scripting: Fix compile when python is not found
  * obs-ffmpeg: Fix unpause causing certain encoders to fail
  * libobs: Add function to get encoder pause offset
  * UI: Don't reselect SceneTree items if tree is clearing
  * UI: Remove executable bit from public key file
  * obs-ffmpeg: Fix m3u8 recording in AMF
  * linux-pipewire: Close sessions as we are done with them
  * libobs/media-io: Restore color range conversion
  * CI: Downgrade Sphinx to fix docs build error
  * libobs/media-io: Avoid scaler for range diff
  * linux-capture: Fixup window name/class checking
  * obs-ffmpeg: Cap AMF encoder at 100 Mbps
  * UI: Fix color of popout icon
  * UI: Fix dock titlebar icons not loading
  * libobs,UI: Swap red/blue render/output channels
  * frontend-tools: Display dialog when changing Python version
  * frontend-tools: Display Python version in UI
  * obs-filter: Update model for NVIDIA Audio FX
  * obs-ffmpeg: Fix when NVENC retries without psycho aq
  * obs-ffmpeg: Show detailed NVENC error messages
  * obs-ffmpeg: use NvEncGetSequenceParams for NVENC header
  * obs-ffmpeg: Refactor NVENC defaults/properties
  * obs-ffmpeg: Update NVENC to new presets
  * obs-ffmpeg: Refactor NVENC
* Tue Oct 25 2022 Hans-Peter Jansen <hpj@urpla.net>
- Enable jack explicitely (it's not detected properly otherwise)
* Sat Oct 22 2022 hpj@urpla.net
- Update to version 28.0.3:
  * win-wasapi: Fix Stop hang
  * frontend-tools: Display dialog when changing Python version
  * frontend-tools: Display Python version in UI
  * UI: Fix AutoRemux not working when FFmpeg output configured
  * win-wasapi: Don't reconnect when inactive
  * libobs: Update version to 28.0.3
  * obs-scripting: Fix compile when python is not found
  * obs-ffmpeg: Fix unpause causing certain encoders to fail
  * libobs: Add function to get encoder pause offset
  * UI: Don't reselect SceneTree items if tree is clearing
  * UI: Remove executable bit from public key file
  * obs-ffmpeg: Fix m3u8 recording in AMF
  * linux-pipewire: Close sessions as we are done with them
  * libobs/media-io: Restore color range conversion
  * CI: Downgrade Sphinx to fix docs build error
  * libobs/media-io: Avoid scaler for range diff
  * linux-capture: Fixup window name/class checking
  * obs-ffmpeg: Cap AMF encoder at 100 Mbps
  * UI: Fix color of popout icon
  * UI: Fix dock titlebar icons not loading
* Sat Sep 24 2022 Hans-Peter Jansen <hpj@urpla.net>
- Disable cef for other than x86_64 archs
- Disable i586 builds
- Improve cef_binary handling
- Build with C++17 standard
* Sat Sep 24 2022 Hans-Peter Jansen <hpj@urpla.net>
- Rename and add more luajit engines:
  0002-Include-moonjit.patch -> 0002-Include-diverse-luajit.patch
- Add cef build conditional
- Update to cef_binary_4638_linux64.tar.bz2
- Add some missing deps
- Enable fdupes
- Failed to add/enable libsndio
* Sat Sep 24 2022 hpj@urpla.net
- Update to version 28.0.2:
  * libobs: Update version to 28.0.2
  * obs-filter: Update model for NVIDIA Audio FX
  * UI: Fix crash when removing filter after changing a value
  * obs-transitions: Allow fetching source properties without source
  * mac-avcapture: Allow fetching source properties without source
  * mac-capture: Allow fetching source properties without source
  * coreaudio-encoder: Allow fetching source properties without source
  * UI: Fix Light theme Studio Mode labels and T-bar
  * obs-vst: Make VST editor buttons reflect UI and VST loaded state
  * obs-vst: Add public function to check for load state of VST
  * obs-vst: Fix crash on macOS when no VST bundle was loaded
  * obs-vst: Allow fetching source properties without source
  * mac-virtualcam: Fix distorted virtual cam image when using full range
  * mac-virtualcam: Fix virtualcam video on Intel-based Macs
  * UI: Update volume controls decay rate on profile switch
  * mac-capture: Undeprecate traditional capture sources on macOS 12
  * CI: Fix Xcode selection in new runner image
  * CI: Switch to Xcode Beta
  * libobs/util: Reject plugins linking Qt5 library for Linux
  * CI: Fix service check workflow using outdated cache
  * UI: Refine YouTube dialog
  * obs-outputs: Drop unused config file
  * rtmp-services: Add Livepush to service list
  * libobs: Add support for reading NV12/YUY2 PQ/HLG
  * w32-pthreads: Add pthread.h as public header
  * libobs-opengl: Disable deprecation warnings on macOS
  * UI: Fix source name edit textbox not accepting input on enter
  * UI: Ignore left-click on non-multiview projectors
  * cmake: Fix rundir installation accepting DESTDIR environment variable
  * linux-v4l2: Remove redundant non-NULL check on FILE
  * linux-v4l2: Fix resource leak on device open error path
  * cmake: Fix CMake package files not being installed on FreeBSD
  * deps: Fix broken prefix for obspython binary module on Linux
  * UI: Fix hotkey settings screen not accepting all input on macOS
  * libobs: Add support for reading I420 HLG
  * linux-capture: Ensure name pixmap is checked
  * UI: Don't mark all widgets in main window as native on macOS
  * UI: Remove spacing from scene and source tree
  * image-source: Update media states when source is de-/activated
  * UI: Don't save/overwrite browser docks if CEF hasn't loaded
  * graphics-hook: Print DXGI swap chain desc
  * graphics-hook: Remove unused code
  * libobs/media-io: Create scaler in more cases
  * decklink: Set output range and color space
  * decklink-output-ui: Set preview color range
  * libobs: Remove unnecessary branch
  * win-capture: Remove unused wildcard code
  * obs-ffmpeg: Fix memory leak with mpegts
  * UI: Fix non-Windows vstrprintf
  * cmake: Fix Sparkle framework permissions
  * UI/updater: CMake: Add /utf-8 to MSVC command line
  * UI/updater: Fix manifest XML namespace for dpiAware setting
  * libobs-winrt,win-capture: Allow forcing SDR
  * image-source: Add JXR HDR support to slide show
  * Revert "UI: Remove "Resize output (source size)" menu"
  * libobs: Update version to 28.0.1
  * UI/updater: Only run updater on Windows 10+
  * win-dshow: Update libdshowcapture
  * Revert "win-dshow: Save and restore video device config props"
  * decklink: Keep deckLinkConfiguration while in use
  * decklink: Remove unnecessary AddRef
  * obs-ffmpeg: Fix seek offset being calculated incorrectly
  * UI/updater: Fix files with similar hashes clashing
  * UI/updater: Fix silent failure on auto-update
  * UI/updater: Fix wrong parameter order for MessageBox
  * UI/updater: Use a unique temp path for patch files
  * win-dshow: Fix avermedia HDR tonemapping
  * UI: Remove button box setIcon
  * UI: Fix Previous icon in System
  * UI: Fix padding on context bar buttons in Dark
  * UI: Fix scene list crash
  * libobs: Update version to 28.0.0
  * UI: Fix "Stop Virtual Camera" button color
  * obs-ffmpeg: Always reset timestamp
  * UI: Remove reset-timestamp option
  * UI: Fix missing files warning icon
  * UI: Fix context bar being squished
  * UI: Remove individual sources (for now) from vcam config
  * obs-ffmpeg: NVENC "(new)" begone
  * plugins: Update obs-websocket to 5.0.2 (Crowdin translations)
  * libobs-opengl: Use a simple 24bit framebuffer
  * UI: Fix properties tool button styling
  * UI: Make list widget styles consistent
  * UI: Fix styling of buttons in scene switcher dialog
  * UI: Add HTTP header if the update check is manually initiated
  * Update translations from Crowdin
  * UI: Fix source tree hovering being inconsistent
  * UI: Show sizing grip in dialogs where resizing is useful
  * UI: Use QDialog for all dialogs
  * UI/updater: Delete files listed as removed in manifest
  * obs-ffmpeg: Log codec when creating NVENC encoders
  * UI: Fix padding on context bar buttons in System and Dark themes
  * obs-ffmpeg: Rename NVENC type for clarity
  * obs-ffmpeg: Fix NVENC HEVC regression
  * UI: Fix scene list spacing (#7202)
  * UI: Get correct coordinates for items in Scene Grid Mode
  * UI: Fix scrollbar enablement in Scene Grid Mode
  * UI: Resize SceneTree after dropEvent
  * UI: Change groupbox radius
  * UI: Make settings margins consistant
  * UI: Fix position of Sources dock actions on horizontal resize
  * plugins: Rename Partial to Limited in localization files
  * obs-ffmpeg: Add AVContentLightMetadata to MPEG-TS
  * libobs: Extend NVIDIA anti-flicker to desktops
  * obs-ffmpeg: Don't use NVENC async mode
  * UI: Add workaround for scenes being unselected
  * mac-capture: Remove explicit call to setBackgroundColor
  * obs-ffmpeg: Fix NVENC async usage pattern
  * UI: Fix crash with adding source
  * UI: Fix source item widget color height
  * obs-filters: Clarify that HDR Tone Mapping filter is optional
  * libobs: Avoid display clear workaround if possible
  * libobs: Increase texture encode buffering
  * obs-ffmpeg: In AMF, use bframe count + 1 as DTS offset
  * obs-ffmpeg: Set max AMF consecutive bframes to 3 by default
  * obs-filters: Fix HDR tonemap filter for scRGB
  * mac-capture: Replace false with 0
  * UI: Widen Edit Transform inputs to fit suffix in Yami
  * rtmp-services: Update Streamvi
  * UI: Fix small font size on macOS and fallback font
  * UI: Copy va_list in strprintf on non-Windows
  * UI: Force expand.svg in menu arrows
  * UI: Increase QGroupBox title padding
  * UI: Unify context menus
  * UI: Cleanup QMenu QSS
  * UI: Unify all border radii
  * libobs: Use system header notation for pthread.h include
  * obs-ffmpeg: Change AMF bitrate to kbps
  * UI: Simplify multiview projector removal
  * UI: Remove allProjectors list
  * UI: Fix extra browsers trash icon
  * UI: Fix crash when toggling volume control mode
  * libobs-opengl: Fix Mac projector color space
  * libobs: Fix Windows 10/11 Gamemode/HAGS detection
  * libobs: Emulate clear with draw for displays
  * UI: Fix color select buttons with Yami
  * CI: Bump Linux CEF build to disable GTK
  * UI: Force fixed font in plain text edits
  * mac-capture: Use cleaner render patterns
  * UI: Fix scripts dialog buttons
  * UI: Fix disabled sliders color
  * UI: Fix fields not growing in FFmpeg output settings
  * UI: Use bigger default size for button dock
  * obs-ffmpeg: Fix AMF encoder lockup with older AMD cards
  * obs-ffmpeg: Use AMD example PTS/DTS offset
  * cmake: Set RELEASE_CANDIDATE/BETA based on git describe
  * ffmpeg-mux: Do not output error if non-fatal error
  * Revert "ffmpeg-mux: Disable stdout/stderr on Windows"
  * ffmpeg-mux: Disable stdout/stderr on Windows
  * UI/installer: Update references to dependencies for 28.0.0
  * UI: Remove separate trash icon themeID
  * UI: Properly register VoidFunc in Meta Object System
  * mac-capture: Clip gamut to sRGB
  * UI: Reset volume/media sliders on theme change
  * Revert "flatpak: Install CMake config files"
  * flatpak: Avoid cleaning all pkgconfig files
  * CI: Update Flatpak image to KDE 6.3
  * cmake: Fix missing interface include directory on Framework export
  * UI: Use backspace icon to indicate "Clear" in hotkey-edit
  * mac-capture: Add missing locale text
  * rtmp-services: Remove defunct servers/services
  * libobs: Initialize main_view video mix before video thread
  * obs-ffmpeg: Fix ffmpeg_output memory leak
  * Revert "libobs: Correctly set texture size"
  * win-dshow: Incorporate Elgato submodule
  * UI: Check for virtual camera enablement before loading config
  * libobs: Correctly set texture size Correctly set texture size according to the frame to be rendered this time. Fixes the mismatch between frame and texture when async-delay-filter on.
  * UI: Remove spaces from translation keys
  * Revert "UI: Don't set theme if it didn't change"
  * UI: Correctly draw sub-item SpacingHelper on group
  * UI: Don't show sub-item SpacingHelper on locked group
  * UI: Save virtual camera outside of the modules object
  * UI: Reintroduce faster theme switching
  * UI: Remove unused stylesheet code
  * UI: Free virtual cam memory on shutdown
  * obs-x264: Remove unused HDR code
  * libobs-d3d11: Unbind framebuffer before Present
  * UI: Only set QStyle on app start
  * UI: Don't set theme if it didn't change
  * linux-v4l2: Correct udev fd poll event test
  * UI: Use user application support as base_module_dir
  * UI: Only load legacy macOS .so plugins on x86_64
  * UI: Don't load macOS plugin bundles from global library
  * UI: Fix crash when hiding audio mixer item
  * obs-qsv11: Do not apply limits if CPU generation is unknown
  * obs-ffmpeg: Add b-frame logging for AMD encoder
  * UI: Fix use-after-free in properties view
  * libobs: Use nal_ref_idc for H.264 priority
  * plugins: Update translations from Crowdin
  * Update translations from Crowdin
  * obs-ffmpeg: Prevent invalid NVENC combinations
  * linux-v4l2: Check udev fd events
  * UI: Update windowaudio.svg
  * UI: Update icons for interact and refresh
  * libobs: Read /etc/os-release on FreeBSD
  * rtmp-services: Update Switchboard Live service (#7104)
  * CI: Build ALSA support on FreeBSD
  * aja: Correct typos in README.md
  * obs-ffmpeg: Block 8-bit HDR for AV1 encoders
  * obs-x264: Block 10-bit formats
  * obs-filters: Don't allow HDR max below 5 nits
  * obs-qsv11: Replace CRITICAL_SECTION with SRWLOCK
  * obs-qsv11: Prevent 8-bit HDR, and 10-bit anything
  * obs-ffmpeg: Prevent invalid AMF combinations
  * obs-ffmpeg: Fix leaks in AMF with unique_ptr
  * UI: Fix theme leak
  * CI: Remove UNIX_STRUCTURE from FreeBSD Cirrus-CI config
  * UI: Fix settings properties view background on Yami variants
  * UI: Fix grid mode spacing with Yami variants
  * UI/themes: Disable QDialog button icons on Yami new variants
  * UI: Fix Yami list widget hover color
  * UI/themes: Add macOS separator fix to Dark and System
  * UI: Add Yami variants for Acri and Rachni
  * UI: Add Yami greyscale variant
  * UI: Add Yami light variant
  * UI: Add missing Icon in System theme
  * linux-v4l2: Add eventfd to signal udev on shutdown
  * libobs: Fix format specifier warning
  * UI: Fix increment check for what's new (again)
  * UI: Remove #if expression for what's new message
  * UI: Add Whats New for macOS/Linux
  * win-dshow: Move invalid GUID warning
  * win-dshow: Fix building without Virtual Camera
  * README.rst: Update url of translation guide
  * README.rst: Update Crowdin Badge url
  * CI: Switch to included Xcode 14 Beta
  * UI: Fix grid mode spacing with Yami
  * UI: Fix settings properties view background
  * win-capture: Fix memory leak in dc-capture.c
  * CI: Update FreeBSD Cirrus-CI configuration
  * UI: Fix memory leak when virtualcam fails to start
  * libobs: Fix gpu thread termination when additional video mixes are added
  * UI: Fix crash when pausing/unpausing recording
  * obs-filters: Fix filter color space queries
  * libobs: Fix filter color space passthrough
  * mac-virtualcam: Don't convert color space when converting color format
  * mac-virtualcam: Avoid conversion of P010
  * obs-filters: Add HDR Tonemap filter
  * UI: Fix padding with vertical volume meters
  * UI/themes: Disable QDialog button icons on all non-system themes
  * decklink: Remove BOM
  * libobs: Remove unnecessary UTF characters
  * deps/w32-pthreads: Remove unnecessary UTF characters
  * UI: Remove unnecessary UTF character
  * obs-ffmpeg: Fix format specifier in obs-amf-test
  * .gitignore: Add install_temp folder
  * docs/sphinx: Update references to Python 3.x
  * libobs-d3d11: Force SDR for legacy swap chain
  * UI: Avoid forcing the user to start the virtual camera
  * UI: Cleanup virtual camera config dialog code
  * obs-filters: Remove param from AI greenscreen
  * enc-amf: Mark as deprecated
  * obs-ffmpeg: Add b-frame option to AMF encoder
  * libobs: Remove display GPU markers without draws
  * obs-filters: Support HDR AI greenscreen
  * cmake: Update pluginhelpers script from obs-plugintemplate
  * cmake: Update Xcode project generation on macOS
  * cmake: Fix unwanted public header installation on macOS
  * cmake: Remove workarounds for legacy obs-browser submodule
  * cmake: Fix missing header installation for libobs and obs-frontend-api
  * mac-videotoolbox: Fix typo 'diffent'
  * cmake: Fix CMake package export templates for CMake 3.24
  * libobs-opengl: Check window creation for errors
  * mac-videotoolbox: Reject color formats other than NV12 and I420
  * mac-capture: Fix macOS 12 SCK Display Capture workaround
  * UI: Fix build error with stray defaultStylesheet
  * UI/installer: Require Windows 10 64bit minimum
  * Revert "UI: Apply default stylesheet before applying theme"
  * win-capture: Fix incorrect path in CMakeLists
  * cmake: Fix M1-based OBS.app appearing as being an "iOS" app
  * cmake: Fix broken pthread detection on Windows with CMake 3.24
  * obs-filters: Fix NVIDIA greenscreen issues
  * obs-scripting: Fix SWIG flags for non-macOS POSIX
  * UI: Fix ffmpeg path browse button not showing
  * obs-ffmpeg: Set NVENC CQP maximum to 51
  * libobs, win-capture: Don't export ms_get_obfuscated_func
  * obs-browser: Update version to 2.18.5
  * cmake: Fix plugin RPATH entry on Linux
  * libobs: Fix missing pair of GS_DEBUG_MARKER
  * obs-filters: Reset RTX greenscreen on cuda error
  * obs-ffmpeg: Fix USAGE typo
  * win-wasapi: Add missing locale text
  * flatpak: Use FFmpeg GitHub mirror
  * UI: Fix spacing with media controls
  * obs-ffmpeg: Remove unused variables for NVENC
  * obs-ffmpeg: Reinit before retrying init for NVENC
  * obs-ffmpeg: Correctly assign argument for NVENC When retrying again without Psycho Visual Tuning, the argument psycho_aq should be false.
  * UI: Fix buttons in settings dialog
  * obs-ffmpeg: Add better error if SRT or RIST libraries are not found
  * libobs: Prevent D3D11 projectors from tearing
  * UI: Fix spacer lines not using accessibility color
  * UI: Fix typo "QTestEdit" in Yami
  * UI: Make spacing helpers DPI aware
  * test: Only build osx tests for OS_MACOS
  * UI: Increase maximum limit of automatic file splitting
  * cmake: fix default version if `git describe` fails
  * Revert "linux-capture: Fix Ubuntu 21.10 builds"
  * UI: Unregister file splitting hotkey when clearing hotkeys
  * obs-ffmpeg, obs-transitions: Use property suffixes
  * UI: Don't hardcode margins in lineedit-autoresize
  * mac-capture: Show "hidden" checkbox for app capture on update as well
  * CI: Fix Flathub workflow tag validation
  * CI: Fix Steam workflow for APFS DMGs
  * CI: Update Steam workflow for Apple Silicon builds
  * CI: Fix checking xcode url secret availability
  * obs-scripting: Fix issues between runtime and compile-time versions
  * CI: Install Xcode 14 beta for tagged builds
  * aja: Fix output of garbage video during preroll
  * aja: Adjust delay when sending frames to card
  * UI: Add missing Icon in Acri theme
  * UI: Add missing Icon in Rachni theme
  * UI: Properly store manual file splitting type
  * rtmp-services: Remove useless supported codec field
  * rtmp-services: Add fallback to H264 if no supported codec found
  * rtmp-services: Fix incompatible-pointer-types warnings
  * UI: Make audio icons consistent
  * UI: Revamp empty state of SourcesTree
  * UI: Remove 1px spacer from SourceTree
  * UI: Adjust list style of filters dialog
  * UI: Add specific icons to expand and collapse
  * UI: Rename expand.svg to right.svg
  * UI: Remove fixed icon sizes from SourceTree
  * UI: Adjust list style of scenes and sources
  * UI: Adjust list style of settings sidebar
  * UI: Increase maximum size of settings' sidebar
  * UI: Set sidebar icon size to 16px
  * UI: Rework icons
  * obs-websocket: Update submodule
  * CI: Update deps to obs-deps 2022-08-02 release
  * CI: Fix packaging scripts
  * aja: Remove unused code from output plugin
  * obs-amf-test: Add 2.5 second timeout for AMF test process
  * obs-ffmpeg: Throw on invalid amf_format
  * obs-ffmpeg: Use get_buf function to ensure buffers_mutex is locked
  * obs-ffmpeg: Fix typo in min_qp_p / max_qp_p options
  * obs-ffmpeg: Don't load AMF DLL before amf-test
  * CI: Change build file names
  * media-playback: Fix crash on free
  * obs-ffmpeg: Use new priority parsing for HLS
  * libobs: Implement H.264/HEVC priority parsing
  * UI: Fix crash if there is no monitoring available
  * obs-ffmpeg: Fix incompatible-pointer-types warning
  * obs-ffmpeg: Replace ftime on *nix platforms
  * UI: Remove compatibility for QT < 5.10
  * obs-ffmpeg: Make muxers respect ENABLE_HEVC
  * UI: Restore color format/space warning
  * win-wasapi: Don't log if reconnect fails
  * obs-ffmpeg: Implement priority for HEVC over HLS
  * libobs: Implement obs_parse_hevc_packet
  * libobs: Consolidate H.264 priority scheme
  * Update translations from Crowdin
  * UI: Add Virtual Camera source selector dialog
  * libobs: Format changes for multiple video mixes
  * libobs: Add support for multiple video mixes
  * CI: Use Qt6 by default when available
  * UI: Fix Qt call on UI thread from graphics thread
  * UI: Add macOS permissions window
  * UI: Add function to open privacy preferences on macOS
  * cmake: Remove prefix suppression for scripting plugins.
  * flatpak: Change obs-deps tag to 2022-07-29
  * flatpak: Avoid cleaning PipeWire and FFmpeg headers
  * flatpak: Update deps based on obs-deps 2022-07-28
  * flatpak: Update KDE Runtime to version 6.3
  * UI: Fix toolbutton colour in Yami
  * UI: Include OpenSans font with OBS
  * UI: Add audio mixer toolbar
  * cmake: Switch file system used by CPack for disk image to APFS
  * mac-videotoolbox: Remove guard for hardware acceleration check
  * CI: Increase macOS deployment target to 10.15 for x86_64
  * UI: Remove permission code paths for Mac OS X before 10.15
  * libobs-opengl: Fix error message for invalid IOSurface buffers
  * mac-syphon: Remove all syphon-inject code
  * mac-capture: Remove display name code path for Mac OS X before 10.15
  * mac-capture: Remove guard for Mac OS X 10.10
  * mac-capture: Remove codepath for discovering devices pre Mac OS X 10.15
  * mac-capture: Remove presets for Mac OS X pre 10.15
  * UI: Add toolButton styling property for buttons
  * obs-ffmpeg: Use top-left chroma location for HDR
  * libobs: Use left chroma location for SDR
  * UI: Fix panning when preview scaling is enabled
  * obs-filters: Add HDR support to Scroll
  * obs-transitions: Add HDR support to stinger
  * obs-ffmpeg: Mark rist/srt required
  * UI: Show spacing helpers in preview
  * mac-capture: Make background transparent in SCK App Capture on macOS 13+
  * enc-amf: Add 2.5 second timeout for AMF test process
  * obs-websocket: Update submodule
  * plugins: Make CMake fail if obs-websocket is not found
  * win-dshow: Compute HDR colorspace
  * media-playback: Compute HDR colorspace
  * CI: Fix Linux package filename version
  * obs-filters: Reset RTX Greenscreen if parent is updated
  * libobs,docs: Improve failed module loading logging
  * CI: Fix Sparkle cache location for local macOS CI build
  * CI: Bump CEF from 4638 (95) to 5060 (103)
  * aja: Only allow output formats matching OBS framerate
  * UI: JXR screenshots on Windows
  * obs-filters: Add HDR support to Crop/Pad
  * obs-filters: Align scale filter to pattern
  * obs-filters: Add HDR bypass for sharpen
  * obs-filters: Add HDR support to Render Delay
  * UI: Fix close display before native surfaces
  * obs-transitions: Simplify fade shaders
  * UI: Fix studio mode label not updating
  * CI: Use xcrun notarytool instead of xcnotary
  * cmake: Add informal output of Qt version selected for current build
  * CI: Add Invoke-External functions for Powershell
  * CI: Disable new mpegts output for linux
  * obs-ffmpeg: Allow use of old mpegts output
  * obs-ffmpeg: Native SRT/RIST for mpegts output
  * mac-capture: Don't exclude desktop windows in SCK display capture
  * mac-capture: Inline content_changed function
  * UI: Add hotkey to split file
  * UI: Add file splitting option "Only split manually"
  * obs-ffmpeg: Enable file splitting with obs_data directly
  * rtmp-services: Add Streamvi service
  * obs-frontend-api: Add function for manual file splitting
  * obs-ffmpeg: Add proc handler for manual file splitting
  * UI: Add support for theme meta, parent theme palette
  * image-source: Correctly assign hotkey to next instead of prev
  * UI/themes: Add image to QGroupBox checkbox on Yami
  * obs-ffmpeg: Set MaxCLL/MaxFALL for AMF
  * win-capture: Bump graphics hook version to 1.8.0
  * graphics-hook: Bump Vulkan version
  * graphics-hook: Relax Vulkan allocation strategy
  * graphics-hook: Update VkResult strings
  * graphics-hook: Track DXGI status with counter
  * graphics-hook: Avoid conflict between Vulkan and DXGI Present
  * CI: Update deps to obs-deps 2022-07-29 release
  * docs/sphinx: Override RTD style
  * docs/sphinx: RTD-friendly documentation changes
  * CI: Update docs to Sphinx v3, fix warnings
  * docs/sphinx: Enable extlinks for shorthand URLs
  * CI: Use ReadTheDocs theme for Sphinx docs
  * rtmp-services: Add WpStream service (#6784)
  * UI: Set default theme to Yami
  * libobs: Include plugin path in log error message
  * UI: Show warning on plugin load failure
  * libobs: Add obs_load_all_modules2 and obs_find_modules2
  * libobs/util: Add get_plugin_info (internal)
  * libobs: Add currently used Qt version to obsconfig.h.in
  * libobs: Remove funcs/structs to "load all modules" from SWIG
  * libobs/util: Put module load detection in its own func
  * UI: Deduplicate UI element names
  * plugins: Add obs-websocket submodule
  * obs-ffmpeg: Fix frame remain after changing file After changing the media source from video file to audio file, the last video's frame (preloaded) maybe still rendered.
  * libobs: Rename "Mac OS X" to "macOS" in log
  * UI: Remove unused header for macOS
  * UI: Search combo item with QVariant type
  * UI: Clean up Settings Output form
  * UI: Respect DPI for preview interactions
  * UI: Add scene item rotation handle
  * UI: Make status bar inactive icons color-blind safe
  * UI: Add Accessibility menu to settings
  * UI: Change crop border line style
  * libobs: Remove redundant get_data calls in obs_data functions
  * UI: Fix macOS permissions availability check
  * libobs: Fix crash handler noreturn compiler warning
  * deps/obs-scripting: Ignore base_set_crash_handler
  * CI: Use VS2022 and clang-format 13
  * libobs: Remove unused cmake configure files
  * UI/forms: Improve macOS dock overlay icons
  * UI: Fix missing file list not including transitions
  * UI: Fix bugs with missing files refactor
  * CI: Fix clang-format if path has spaces
  * obs-vst: Remove submodule in favour of direct merge 2/2
  * obs-vst: Remove submodule in favour of direct merge 1/2
  * mac-capture: Fix creation of invalid window stream on source creation
  * mac-capture: Fix issue with desktop capture introduced by macOS 12.5
  * mac-capture: Cleanup code to improve efficiency
  * mac-capture: Fix availability on macOS 12.5
  * UI: Omit stream codecs the service doesn't support
  * UI: Refactor simple encoders to a func
  * libobs: Add func to get supported service codecs
  * libobs: Remove trailing whitespace
  * obs-ffmpeg: Add HEVC to supported HLS codecs
  * obs-vst,obs-browser: Update submodules
  * aja-output-ui: Add Qt::Gui to find_qt on Linux
  * cmake,UI: Refactor find_qt macro
  * UI: Only check major.minor for "what's new"
  * UI: Use separate version string for what's new, save it
  * UI: Clean up OBSBasic::ReceivedIntroJson a bit
  * UI: Ensure thread signal posts to UI thread
  * virtualcam-module: Return S_FALSE if locks non-zero
  * UI/themes: Correctly specify rgb instead of rgba
  * UI: Add File Integrity Check
  * UI: Relatively center multiple scene items
  * mac-capture: Improve SCK locale strings
  * UI: Add scene names to preview/program labels
  * libobs: Rewrite macOS hotkeys implementation
  * UI: Add functions to check for and request macOS permissions
  * obs-vst: Update submodule
  * virtualcam-module: Don't send frames if stopped
  * virtualcam-module: Use OBS atomic funcs
  * virtualcam-module: Only allow DLL unload when filter freed
  * libobs: Set coefficients with higher precision
  * UI: Remove padding on QStackedWidget in Yami
  * obs-filters: Add HDR bypass for various filters
  * obs-filters: Add HDR bypass for color correction
  * UI: Add audioProcessOutputIcon to Yami
  * libobs: Trigger bindings injected by Qt directly
  * libobs: Fix audio monitor output error in macOS
  * UI: Add initialization to ensure compat between pthread and NSThread
  * UI: Add status overlay for macOS dock icon
  * UI/forms: Add macOS specific dock overlay icons
  * obs-ffmpeg: Fix AMD falling back to wrong preset
  * UI: Fix wrong AMD recording preset (simple output)
  * mac-syphon: Disable inject functionality on macOS 10.15+
  * mac-syphon: Fix broken license display button on macOS 11+
  * obs-filter: Add RTX Background Removal filter
  * obs-filter: Add NVIDIA Room Echo Removal to noise suppression filter
  * obs-filter: Fix loading of NVIDIA Audio Effects SDK
  * obs-filter: Update NVIDIA Audio SDK
  * mac-capture: Don't show apps with empty name in SCK
  * mac-capture: Add deprecated flag to traditional captures if SCK exists
  * mac-capture: Add label about missing audio on macOS 12 to SCK
  * mac-capture: Add more verbose log warning for missing permissions
  * mac-capture: Fix compiler warnings for unused variables and data loss
  * mac-capture: Make properties window reactive to selected capture type
  * mac-capture: Increase required macOS version for ScreenCaptureKit
  * Add support in "macOS ScreenCapture" for capturing audio through ScreenCaptureKit in macOS 13. By default, OBS will capture the audio for the frame content its capturing and exclude OBS own audio. For additional information on the capabilities of audio capture refer to the documentation https://developer.apple.com/documentation/screencapturekit/ or watch the session "Meet ScreenCaptureKit".
  * mac-capture: Add support for improved window capture in macOS 12.3
  * libobs: Allow Chrome class executable matching
  * UI: Add application audio capture to toolbar
  * win-wasapi: Add support for capturing a process
  * libobs, win-capture: Share window helper code
  * libobs, UI: Add OBS_ICON_TYPE_PROCESS_AUDIO_OUTPUT
  * libobs/util: Add WinModule RAII wrapper
  * cmake: Enable ENABLE_HEVC by default
  * obs-outputs: Improve librtmp timeouts on Linux
  * UI: Use combobox data field for Theme value in settings
  * UI: Enforce Fusion Qt style on Linux
  * UI: Fix crash on macOS if no python path is set in configuration
  * UI: Remove unused functions for audio mixers
  * obs-outputs: Fix TLS_client init for mbedTLS 3.1.0+
  * UI: Hide network features if a non-RTMP service is set
  * v4l2,scripting: Add more thread names
  * UI: Replace QMessageBox setButtonText with addButton
  * UI: Fix Qt 6 position deprecations
  * UI: Use pipe operator instead of plus for Qt keys
  * deps,libobs,plugins: Fix discarded-qualifiers warnings with FFmpeg 5
  * Use property suffixes for units everywhere
  * obs-browser: Update version to 2.18.2
  * obs-ffmpeg: Fix AMF AVC / HEVC check logic
  * UI: Update simple output to use new AMD encoder
  * obs-ffmpeg: Add texture-based hardware AMD encoder
  * cmake: Fix public header files being installed to rundir
  * frontend-tools: Upgrade legacy Python library paths to modern format
  * cmake: Fix RPATH on Linux for frontend-tools to find obs-scripting
  * obs-scripting: Add support for multiple Python 3 versions
  * obs-scripting: Switch swig to stable ABI usage
  * cmake: Change desired Python3 DLL name to stable ABI variant
  * UI: Suppress LNK4098
  * mac-syphon: Ignore 10.13-only deprecation warning
  * cmake: Add EXCLUDE_FROM_ALL to Linux install_headers
  * cmake: Add PUBLIC_HEADER DESTINATION for development rundir
  * UI: Remove disable_high_dpi_scaling option on Qt 6
  * UI: Add low latency audio buffering mode to UI
  * libobs: Remove OBS_UNUSED
  * aja-output-ui: Avoid using OBS_UNUSED
  * obs-scripting: Replace OBS_UNUSED with UNUSED_PARAMETER
  * libobs-opengl: Replace OBS_UNUSED with UNUSED_PARAMETER
  * plugins: Replace OBS_UNUSED with UNUSED_PARAMETER
  * libobs: Replace OBS_UNUSED with UNUSED_PARAMETER
  * aja: Remove unused parameters
  * obs-ffmpeg: Remove unused parameter
  * libobs: Remove unused parameters
  * deps/opts-parser: Skip parsing of empty strings
  * UI: Fix undo stack uninitialized ui warning
  * aja: Remove unnecessary .keepme files
  * decklink-output-ui: Fix memory leak
  * CI: Update deps to obs-deps 2022-07-18 release
  * UI: Add media control icons to Yami
  * obs-filters: Remove unnecessary OBS_UNUSED attribute
  * plugins: Cleanup unused-parameters
  * UI: Remove unnecessary UNUSED_PARAMETER
  * libobs: Cleanup unused-parameters
  * libobs: Remove set but not read variable
  * cmake: Fix pkgconfig generation
  * mac-videotoolbox: Guard hardware_accelerated check behind macOS 10.14
  * mac-avcapture: Fix null-conversion warning
  * Revert service json lookup refactor in UI
  * text-freetype2: Don't read / write empty size arrays
  * rtmp-services: Avoid calling bmemdup on NULL resolution list
  * UI: Remove duplicate missing files code
  * cmake: Treat warnings as errors on MSVC
  * UI: Disable LNK4099 warning
  * obs-ffmpeg: Fix type mismatch
  * aja-output-ui: Suppress C4996
  * aja: Suppress C4996
  * text-freetype2: Suppress LNK4098
  * obs-outputs: Suppress LNK4098
  * obs-filters: Suppress LNK4098
  * obs-ffmpeg: Suppress NVENC preset warnings for now
  * obs-browser: Update version to 2.18.1
  * UI: Check output path when starting replay buffer
  * aja: Increment aja-source version for buffering setting
  * UI: Add frame around transitions dock
  * UI: Add menu icons to resource folder
  * deps/media-playback: Fix invalid seek at reset
  * libobs: Fix pulseaudio crash.
  * libobs: Log errors for bmalloc(0)
  * libobs: Deprecate base_set_allocator and make it no-op
  * UI: Correctly spell "ChromeOS" again
  * UI: Fix menu icons not showing up
  * obs-qsv11: Fix timestamp for fractional frame rate
  * UI: Fix color format warning
  * CI: Update deps to obs-deps 2022-07-08 release
  * obs-scripting: Fix crashes introduced by Swig update to 4.1.0
  * win-capture: Fix subprojects not installing on incremental builds
  * cmake: Fix libraries and header files being installed for packages
  * UI: Fix text shifting on lineEdits
  * CI: Update Ubuntu versions
  * CI: Fix Flatpak releases
  * UI: Add more information to describe output format
  * mac-syphon: Fix usage of methods deprecated since macOS 11.0
  * cmake: Disable LNK4099 warning
  * obs-ffmpeg: Fix warning about useless llabs call
  * aja: Fix warnings about type usage
  * libobs: Fix warnings about type usage
  * obs-scripting: Suppress long volatile warning
  * UI: Use more descriptive tooltips
  * UI: Add Apple H.264 hardware encoder to simple mode
  * mac-videotoolbox: Enable CBR and CRF on hardware encoders only
  * mac-videotoolbox: Add CRF support on Apple silicon
  * mac-videotoolbox: Add CBR support on Apple silicon / macOS 13
  * mac-videotoolbox: Use type_data as it was intended
  * mac-videotoolbox: Remove redundant bitrate check
  * mac-videotoolbox: Rename functions to remove "h264"
  * cmake: Rename mac-vth264 plugin to mac-videotoolbox
  * mac-videotoolbox: Rename mac-vth264 plugin to mac-videotoolbox
  * UI: Implement Taskbar Overlay for Qt6
  * UI: Fix typo with SetSourceName function
  * UI: Fix compiling error on nix platforms
  * UI: Truncate push-to-* labels
  * UI: Use new truncate function with hotkeys
  * UI: Move multiview render into a new class
  * UI: Fix reset ui warning showing on first start
  * libobs-opengl: Change log level for texture_from_pixmap
  * linux-capture: Silence log spam on xcomposite capture
  * linux-capture: Retry capture if texture not created
  * mac-avcapture: Fix deprecation warning for AVCaptureDevice list
  * obs-outputs: Rework RTMP context init/deinit
  * aja: Split audio part in CaptureThread to function
  * aja: Fix memory overrun on aja-source
  * obs_ffmpeg: Explicitly mark variables as unused
  * images-source: Explicitly mark variables as unused
  * aja: Explicitly mark variables as unused
  * libobs: Explicitly mark variables as unused
  * aja-output-ui: Explicitly mark variables as unused
  * libcaption: Disable compiler warnings about non-exhaustive switch cases
  * libobs: Disable compiler warnings about non-exhaustive switch cases
  * obs-ffmpeg:  Disable compiler warnings about non-exhaustive switch cases
  * obs-filters: Disable compiler warnings about non-exhaustive switch cases
  * obs-x264: Disable compiler warnings about non-exhaustive switch cases
  * obs-ffmpeg: Fix srt/rist not working
  * aja: Fix audio capture sometimes offset by a channel
  * obs-qsv11: Use same adapter as OBS
  * UI: Yami font adjustments
  * obs-ffmpeg: Add NVIDIA Tesla NVENC support
  * obs-ffmpeg: Add m4v extension to open file dialog
  * CI: Switch to universal Qt builds for CI
  * obs-scripting: Fix swig runtime header generation for macOS
  * docs: Fix encoder .get_defaults2 arguments
  * UI: Fix compilation with browser disabled
  * cmake: Fix build architectures and deployment target not set to defaults
  * UI: Apply default stylesheet before applying theme
  * UI: Don't re-apply theme when saving Settings
  * UI: Remove OBSBasic.ui.autosave
  * UI: Add new theme Yami
  * deps/obs-scripting: Log script load/unload
  * UI: Fix network feature visibility after loading settings
  * cmake: Fix hardcoded SWIG_DIR path on macOS
  * libobs: Remove newlines on ends of fixed audio buffering message
  * UI,mac-avcapture: Use consistent variables in locales
  * UI: Remove unused undo/redo strings
  * UI: Make properties window default to 50/50 split
  * UI: Move HDR units for settings to suffix
  * UI: Fix YouTube Chat build failure with Qt 6
  * CI: Fix git usage inside Flatpak action container
  * rtmp-services: Update Piczel.tv recommended settings
  * UI: Add ability to send messages to YouTube chat
  * UI: Add SendChatMessage to YouTube API wrappers
  * UI: Add vertically expanding LineEdit Widget
  * linux-pipewire: Log modifier
  * libobs,UI,docs: Add info as text property sub-type in the property API
  * UI: Try closing remux before initiating shutdown
  * UI: Add ability to reset whole UI
  * UI: Hide network features if a non-RTMP service is set
  * UI: Change default reconnect values
  * libobs: Improve exponential backoff functionality
  * UI: Only offer ultrafast-fast x264 presets in Simple Mode
  * UI: Move Simple Mode encoder preset out of Advanced
  * UI: Move Simple Mode audio bitrate above encoder
  * CI: Use static 7zip build instead of PPA
  * mac-vth264: Fix PTS passed to the encoder
  * rtmp-services: Add Mildom and Nonolive
  * mac-virtualcam: Fix IOSurface memory leak
  * mac-avcapture: Make "High" preset default
  * UI: Fix crash if missing module in context bar
  * obs-ffmpeg, obs-outputs: Check return of obs_encoder_get_extra_data
  * UI: Fix cut transition not being initialised
  * UI: Fix formatting
  * UI: Support pressing space to open MenuButton
  * UI: Use existing IsThemeDark() in more places
  * linux-pipewire: Shuffle screencast D-Bus proxy around
  * linux-pipewire: Cleanup includes
  * linux-pipewire: Move all portal code to screencast-portal.c
  * linux-pipewire: Introduce proxy struct for screencast portal
  * linux-pipewire: Shuffle some code around
  * linux-pipewire: Rename pipewire-capture to screencast-portal
  * linux-pipewire: Always load PipeWire captures
  * linux-pipewire: Remove unused variable
  * UI: Regroup and Reorder source right-click menus
  * UI: Only show "Interact" menu for interactable sources
  * UI: Remove "Resize output (source size)" menu
  * UI: Move transition duration above Add/Remove buttons
  * Revert "UI: Redesign transitions dock"
  * Revert "UI: Fix "Add [transition]" not being translated"
  * Revert "UI: Move "Add [transition]" to bottom of combo"
  * Revert "UI: Fix non-default transitions going below add vals"
  * Revert "UI: Fix selecting correct transition when deleting"
  * Partly revert "UI: Fix Qt signal connection warnings"
  * obs-outputs: Don't shutdown RTMP session when silently reconnecting
  * cmake: Fix handling of optional debug wrapper libraries for obs-browser
  * obs-browser: Don't auto-focus, remove init hack
  * UI: Use libobs rosetta detection
  * libobs/util: Add function to get Rosetta translation status
  * aja: Implement buffering property
  * deps/media-playback: Fix metadata for hw_accel
  * UI: Cleanup advanced audio window
  * CI: Update obs-crowdin-sync to 0.2.1
  * linux-v4l2: Add support for H.264
  * mac-virtualcam: Free virtualcam data when destroying
  * win-dshow: Save and restore video device config props
  * linux-pipewire: Restore PipeWire minimim version requirement
  * obs-outputs: Fix missing function declaration
  * obs-outputs: Reset TLS on reconnect
  * UI: Add eventFilter to media slider
  * decklink: Avoid sending 0x0 frame to libobs
  * UI: Make transform dialog spinboxes consistant
  * UI: Fix position of reset filters button
  * UI: handle theme file names with "." characters
  * obs-ffmpeg: Remove codec property from VAAPI encoder
  * mac-virtualcam: Fix CMIO errors due to unsettable properties
  * mac-virtualcam: Fix port leakage in Mach server
  * mac-virtualcam: Do not rely on global state
  * mac-virtualcam: Remove unused CMSampleBuffer utility functions
  * mac-virtualcam: Prevent output conversion if possible
  * mac-virtualcam: Support multiple AV planes
  * mac-virtualcam: Pool pixel buffers
  * mac-virtualcam: Use IOSurface to share output with virtual cameras
  * mac-virtualcam: Build DAL plugin for ARM64e target as well
  * libobs-opengl: Remove unnecessary call to retrieve screen number
  * libobs-opengl: Remove unused code
  * UI: Fix multithread-unsafe GetCurrentScene
  * obs-outputs: Clear RTMP data before initiating connect
  * CI: Fix FreeBSD definition of streaming service
  * UI: Simple Output Mode for NVENC HEVC
  * libobs: And fix area scaling effect with RGBA
  * docs/sphinx: Minor formatting corrections
  * docs/sphinx: Update configuration and version
  * docs/sphinx: Update GitHub links to OBSProject org
  * libobs: Fix bilinear lowres RGBA as well
  * libobs: Fix RGBA format output not working
  * rtmp-services: Remove defunct servers/services
  * libobs: Deprecate obs_hotkey_enable_strict_modifiers
  * libobs: Clear low bits when writing P010
  * libobs: Ensure active copy surfaces are active
  * flatpak: Update deps based on obs-deps 2022-05-23
  * UI: Mark YouTube window showEvent as override
  * UI: Fix unused parameter warnings
  * CI: Update deps to obs-deps 2022-05-23 releases
  * rtmp-services: Update Eventials ingests
  * UI: Fix crash when pressing `tab` key in rename
  * docs/sphinx: Fix statement typo for bfree()
  * UI: Use int return type in OBSIgnoreWheelProxyStyle
  * obs-ffmpeg: Add a circlebuf to buffer output in ffmpeg-mux
  * flatpak: Install CMake config files
  * UI: Truncate names in advanced audio dialog
  * libobs: Fix issue 4408 (hotkey logic)
  * UI: Close display before native surfaces
  * obs-scripting: Fix missing frontend bindings for Python
  * obs-scripting: Fix missing frontend bindings for Lua
  * libobs: Fix rendering null sprite
  * cmake: Fix enabling PulseAudio monitoring
  * obs-x264: Use period for localized sentence
  * obs-ffmpeg: Use period for localized sentences
  * libobs/util: Add %%s string replacement for unix time
  * obs-x264: Convey lack of Rec. 2100 support
  * obs-ffmpeg: Localize NVENC error dialog messages
  * obs-ffmpeg: Improve dialog text for NVENC errors
  * UI: Add suffixes to transform dialog
  * win-dshow: Removed used UNUSED_PARAMETER
  * deps/media-playback: Use metadata for HDR EETF
  * libobs: Add max_luminance to obs_source_frame
  * win-capture: Rename Rec. 2020 to Rec. 2100
  * deps/glad: Drop glad-glx
  * Drop GLX renderer
  * linux-capture: Drop GLX code paths
  * linux-capture: Fix map-like behavior for watcher
  * mac-avcapture: Capture audio if supported
  * CI: Update service-removal PR description
  * CI: Ping authors of failed services in removal PR
  * libobs: Fix hotkey with right-side modifiers
  * UI: Remove m3u8 format from simple output mode
  * obs-ffmpeg: Remove duplicate "FFmpeg Options" locale
  * UI: Don't transition in studio mode if scenes are the same
  * libobs: Only warn when releasing non-NULL source
  * deps/media-playback: Fix video looping
  * decklink-output-ui: Fix crash when stopping preview
  * libobs: Clamp audio NaN to 0.0f
  * rtmp-services: Apply automatic formatting to JSON
  * CI: Add services check job
  * UI: Use correct terminology for Program in Studio Mode
  * CI: Validate JSON Schema of Services files
  * rtmp-services: Add JSONSchema definitions for services
  * UI: Move taskbar overlay functions into platform.hpp
  * obs-ffmpeg: Initialize mapped_res field in nv_texture_init
  * obs-ffmpeg: Reserve jim-nvenc textures buffer space
  * CI: Remove extra whitespace from Steam workflow
  * CI: Update first-party GitHub Actions
  * vlc-video: Fix sign-compare warning
  * UI: Make OAuth base URL configurable
  * obs-ffmpeg: Fix memory leak
  * deps/opts-parser: Add missing c extern for cpp
  * obs-ffmpeg: Set 1000 nits for HLG metadata
  * win-wasapi: Log source name when showing device errors
  * libobs: Default 10-bit video to sRGB instead of PQ
  * libobs: Ignore lower six bits for P010 sources
  * cmake: Use correct capitalization for Qt in messages
  * cmake: Normalize path to QtCore_DIR
  * cmake: Teach CopyMSVCBins to use Qt 5 or 6
  * docs: Update speaker_layout enum values
  * UI: Fix memory leak with Manage Broadcast dialog
  * obs-ffmpeg: Fix 4 channel layout in ffmpeg-mux
  * obs-ffmpeg: Fix for channel layout API change
  * libobs: Fix missing include due to FFmpeg 5 changes
  * UI: Move scene import dialog to the stack
  * obs-ffmpeg: Allow setting FFmpeg options for media sources
  * deps/media-playback: Add support for FFmpeg options for media playback
  * linux-v4l2: Fix camera reconnecting issue
  * linux-capture: Add EGL support for xcomposite
  * libobs-opengl: Add create_texture_from_pixmap for EGL
  * deps/glad: update Glad for EGL with new extensions
  * libobs/media-io: Sleep to next audio time accurately
  * libobs/util: Add os_sleepto_ns_fast
  * libobs: Cap HLG video at 1000 nits
  * libobs: Lock scene to video color space
  * UI: Add rename signal to adv audio dialog
  * UI: Put program on top in vertical studio mode
  * UI: Use Shift instead of Alt for Copy/Paste Transform
  * obs-scripting: Fix macro redefinition warning
  * obs-scripting: Fix loading of scripting libraries with runtime lookup
  * linux-capture: Rewrite xcomposite
  * UI: Find Qt WinExtras only in Qt 5
  * rtmp-services: Add sympla service
  * libobs: Fix reserved word in variable names
  * libobs: Reduce PQ shader math
  * UI: Support JXR image dropEvent on Windows
  * image-source: Support JXR on Windows
  * libobs/graphics: Add color space and WIC support
  * libobs: Allow transitions to mix CCCS sources
  * libobs: Add support for reading I420 PQ
  * libobs: Use tabs in format_conversion.effect
  * UI: Restore portable mode on Windows
  * mac-capture: Improve window capture performance
  * cmake: Fix headers installation
  * libobs: Include HEVC files only if enabled
  * obs-ffmpeg: Fix HEVC include in jim-nvenc
  * vlc-video: Fix video rotation and aspect ratio
  * obs-ffmpeg: Change types to avoid unnecessary casts
  * obs-ffmpeg: Log/fail NVENC for B-frame maximum
  * obs-ffmpeg: Default NVENC HEVC Max B-frames to 0
  * obs-ffmpeg: Fix old NVENC ignoring Max B-frames
  * UI: Redo encoder names now that H.264 isn't alone
  * obs-x264: Restore video encoder name to log
  * obs-x264: Disallow HDR attempts gracefully
  * vlc-source: Fix surround sound not properly downmixed
  * UI: Add "H.264" to simple hardware encoders
  * obs-ffmpeg: Fix NVENC HEVC fallback being H.264
  * vlc-video: Fix compiler warnings
  * mac-vth264: Fix compiler warnings
  * mac-capture: Fix compiler warnings
  * mac-virtualcam: Fix compiler warnings
  * libobs: Fix compiler warnings
  * obs-scripting: Fix compiler warnings
  * libobs: Orient images based on EXIF metadata
  * libobs: Fix sign-compare warning
  * obs-output: Fix compiler warnings
  * obs-ffmpeg: Fix compiler warnings
  * obs-scripting: Fix compiler warnings
  * UI: Fix unused-parameter warnings
  * test: Fix cmocka unused-parameter warnings
  * media-playback: Fix unused-parameter warning
  * linux-v4l2: Fix format-truncation warning
  * UI: Fix configuration path handling for Linux portable builds
  * libobs: Fix `LINUX_PORTABLE` preprocessor macro usage
  * cmake: Fix cURL library handling for updated dependencies
  * CI: Use manifest hash as Flatpak cache key
  * libobs-winrt: Support window transparency for WGC
  * UI: Only use volume scrollbars when needed
  * aja: Fix UHD/4K HDMI output on Kona5-8K firmware
  * obs-libfdk: Enable 7.1 channel surround for Linux
  * obs-outputs: Implement send timeout in librtmp
  * Fix indent on multiline comments
  * libobs/media-io: Preserve video side data on remux
  * obs-ffmpeg: Add content light levels for HDR
  * UI: Do not prefer NV12 for I010/P010
  * obs-ffmpeg: Add I010/P010 as formats for old NVENC
  * CI: Update macOS image to macOS 12
  * cmake: Define ENABLE_HEVC globally if set
  * UI: Allow HEVC streaming
  * obs-ffmpeg: Add HEVC support to NVENC
  * win-dshow: Support HEVC decode
  * libobs: Fix NaNs when using EETF for HLG
  * libobs: Clean up color.effect a bit
  * libobs,obs-outputs: Fix librtmp1 interference
  * libobs,UI: Issue appropriate signals on group / ungroup
  * libobs: Add ability to configure audio buffering latency
  * libobs: Fix debug spam from maxed buffering
  * libobs: Add ability to use fixed audio buffering
  * CI: Respect user-specified build directory
  * obs-transitions: Remove unused shader functions
  * UI: Fix compiler warning when WIN32 is not defined
  * UI/importers: Fix compiler warning
  * libobs-opengl: Fix compiler warning
  * obs-transitions: Fix compiler warning
  * aja: Subtract packet time from audio timestamp
  * win-dshow: Respect TRC of encoded video
  * libobs-opengl: Disable vsync during present
  * cmake: Add option to build hardware HEVC encoders
  * Revert "libobs: Allow null sei in obs_extract_avc_headers"
  * flatpak: Cleanup PipeWire module
  * obs-ffmpeg: Refactor FFmpeg video encoders
  * libobs/util: Add ConfigFile::OpenString()
  * libobs/util: Add missing extern "C" header guard
  * libobs: Allow null sei in obs_extract_avc_headers
  * CI: Do not run Steam workflow on forks
  * UI: Remove top level size constraints
  * win-dshow: Add YVYU format
  * obs-ffmpeg: Use YVYU for FFmpeg pix fmt YVYU422
  * deps/media-playback: Use YUV422 for planar 422 pix fmt
  * obs-ffmpeg: Add support for YUV422P10LE, YUV444P12LE, YUVA444P12LE
  * libobs: Add support for YUV422P10LE, YUV444P12LE, YUVA444P12LE
  * obs-ffmpeg: Fix compiler warning
  * libobs: Remove unnecessary blend_type assignment
  * libobs: Fix wrong enum in obs_sceneitem_get_blending_method
  * UI: Use const ref for get_service_from_json()
  * UI: Refactor duplicated streaming page code
  * UI: Prevent auto config service names squishing
  * CI: Add Steam build uploader
  * libobs: Log audio timestamp exceeding TS_SMOOTHING_THRESHOLD
  * obs-transitions: More HDR support
  * libobs: Fix color space auto-convert blending
  * deps/media-playback: Add P010 to closest_format
  * CI: Fix clang-format to include Objective-C
  * obs-ffmpeg: Set P3-D65 metadata for HDR
  * win-dshow: Add reactivation callback
  * win-dshow: Reference new device-vendor.cpp file
  * win-dshow/libshowcapture: Toggle tonemapper according to format
  * UI: Default mixer volume meter to two channels
  * libobs: Make obs_volmeter_get_nr_channels default to 0
  * rtmp-services: Update Bilibili Live
  * UI: Add shortcut for larger movement steps in preview
  * obs-ffmpeg: Add max luminance metadata for PQ
  * deps/media-playback: Use avcodec_free_context to free AVCodecContext
  * cmake: Rename variable in FindPipeWire for clarity
  * cmake: Fix compilation of targets using FindWayland
  * virtualcam-module: Copy Windows virtual camera files to rundir
  * libobs,UI: Support HLG nominal peak level
  * win-capture: Add DXGI/WGC HDR support
  * libobs-winrt: Add winrt_capture_get_color_space
  * libobs-d3d11: Add monitor to HDR status cache
  * UI: Just use json directly for service lookups
  * obs-ffmpeg/ffmpeg-mux: Fix splitting hang on Windows
  * libobs: Remove redundant async_color_format member
  * win-capture: Add HDR support to Game Capture
  * libobs: Add more color handling to default/opaque
  * UI: Fix show/hide toggle with minimize to taskbar
  * win-dshow: Use Rec. 2100 (PQ) by default for P010
  * CI: Use 9-character short hashes in artifact names
  * obs-ffmpeg: Add mxf extension to open file dialog
  * libobs-opengl: Use gl helpers in create_dmabuf_image
  * UI: Set automatic file splitting time in minutes
  * win-dshow: Add Rec. 2020 HLG support
  * obs-filters: Add HDR support to Scaling filter
  * libobs: Rename Rec. 2020 to Rec. 2100
  * deps/media-playback: Fix AVColorSpace usages
  * UI: Create Log Viewer window XML file, migrate code
  * UI: Create Properties window XML file, migrate code
  * libobs, UI: Fix `--verbose` logging for stdout
  * linux-pipewire: Explicitly enumerate portal capture types
  * linux-pipewire: Explicitly enumerate cursor modes
  * linux-pipewire: Move fetching cursor mode to portal.c
  * linux-pipewire: Remove ellipses from log messages
  * linux-pipewire: Properly capitalize log messages
  * linux-pipewire: Log more PipeWire-related info
  * UI: Add high-precision sRGB support
  * deps/media-playback: Add more accurate TRC hints
  * libobs: Add high-precision sRGB support
  * libobs,plugins: Replace video matrix function
  * libobs: Add video_format_get_parameters_for_format
  * linux-capture: Don't initialize format info if init_obs_pipewire fails
  * UI: Add Rec. 2020 space and I010/P010 formats
  * obs-ffmpeg, win-dshow, deps/media-playback: Use recommended API for AVCodecContext
  * libobs: Fix image source not loading upper case file extensions
  * UI: Truncate displayed file paths in the middle in Remux window
  * win-capture: Use normal blend equation for cursor
  * libobs: Clear image on color convert
  * obs-transitions: Smooth source transition fades
  * libobs: Allow transitions to give placeholder
  * rtmp-services: Update AfreecaTV
  * obs-transitions: Add HDR support to cut/fade
  * obs-transitions: Add effect files to VS solution
  * cmake: Fixes plugins not being copied into application bundle on macOS
  * libobs: Fix sign mismatch
  * win-dshow: Add HDR support
  * obs-ffmpeg: Support Rec. 2020, I010/P010 formats
  * deps/media-playback: Add I010/P010 support
  * libobs: Add I010/P010 support, TRC enum
  * libobs: Add color spaces to deinterlace shaders
  * libobs: Add SWS_CS_BT2020 support
  * libobs-winrt: Add null checks to capture
  * aja: Use correct colorspace for SD or HD/UHD
  * obs-filters: Fix scale undistort, attempt two
  * UI: Remove old ComboBoxIgnoreScroll
  * UI: Disable wheel scrolling on QComboBoxes
  * UI: Add support for nonlinear SRGB blending
  * libobs: Add support for nonlinear SRGB blending
  * linux-pipewire: Version check call to pw_deinit
  * cmake: check empty OBS_MODULE_LIST for macOS
  * cmake: Fix configure error on macOS when -DENABLE_SCRIPTING=OFF
  * CI: Update Crowdin Sync to 0.2.0
  * UI: Fix display affinity logic when re-applying
  * win-capture: Fix added resources not properly copied to rundir
  * rtmp-services: Update Stripchat streaming service
  * cmake: Fix usage of relative paths for CEF finder
  * cmake: Fix obs-ffmpeg-mux missing rpath entries for libobs in build tree
  * CI: Fix Windows build scripts relying on localized architecture string
  * cmake: Fix dylibbundler path for case-sensitive partition
  * libobs: Update version to 27.2.4
  * obs-ffmpeg : use I422 for YUV422P input format
  * CI: Add shortened commit hashes to generated artifacts
  * obs-filters: Fix invalid scale filter combination
  * libobs: Add color space management
  * libobs: Add color spaces to scale shaders
  * libobs: Fix stale active_copy_surfaces entries
  * cmake: Fix diverging prefix padding for OBS status outputs
  * UI: Remove unneeded QProxyStyle include
  * CI: Don't ignore deps directory when formatting
  * UI: Add Copy/Paste for source visibility transitions
  * libobs: Unload show/hide transition on load if none
  * libobs: Refactor small bit of code
  * libobs: Refactor hide/show transition functions
  * libobs/util: Remove deprecation visibility from swig
  * deps/obs-scripting: Fix code formatting
  * libobs: Add Rec. 2020 video_colorspace enum values
  * obs-ffmpeg: Use av_packet_alloc instead of av_init_packet
  * UI, file-updater, rtmp-services: Enable curl ALPN support
  * UI: Add missing previousIcon in Rachni theme
  * libobs: Render main texture for active color space
  * UI: Wire up WM_MOVE and WM_DISPLAYCHANGE events
  * libobs: Add obs_display_update_color_space
  * libobs, UI: Add SDR white nits option
  * libobs/graphics: Add gs_is_monitor_hdr
  * libobs/graphics: Add color space support
  * rtmp-services: Fix file mode
  * rtmp-services: Update SharePlay.tv recommendations
  * libobs: Add OBS_COUNTOF for array count
  * cmake: Move obspython.py to Resources on macOS
  * obs-scripting: Add Resources to python path on macOS
  * flatpak: Reenable AJA and JACK plugins
  * UI: Save custom browser docks with docks data
  * UI: Remove UUID from ExtraBrowsersModel
  * UI: Fix custom browser docks UUID
  * libobs: Add array check for deinterlace logic
  * CMake: Fix PDB install directory for library installation
  * CI: Differentiate Linux CI artifact names
  * CI: Update GitHub Actions
  * cmake: Fix targets not being copied into rundir on Windows and Linux
  * libobs/graphics, libobs-d3d11: Add P010 support
  * project: Migrate PipeWire capture into linux-pipewire
  * linux-pipewire: Create new plugin
  * UI: Require Qt Creator's casing for cursorShape in XML validator
  * UI: Fixup minor Qt Creator inconsistencies
  * libobs: Add HEVC parsing functions
  * libobs-d3d11: Remove Intel NV12 whitelist
  * libobs: NV12 textures only for active GPU encoders
  * libobs-d3d11: Make gs_clear honor FRAMEBUFFER_SRGB
  * UI: Fix UI file changes not being picked up by CMake
  * obs-libfdk: Set bitstream to ADTS for mpegts output
  * UI: Remove InitApplicationBundle() function
  * rtmp-services: Add Shareplay.tv
  * obs-outputs,librtmp: Remove encrypted RTMP support
  * librtmp: Add mbedtls 3 compatibility
  * obs-qsv11: Fix double free on CreateSurface failure
  * CI: Update editorconfig to match CMake-format configuration
  * CI: Add 'flatpak' to Flatpak bundle name
  * CI: Fix CMake definition of streaming service options
  * CI: Fix Qt XML Validator workflow
  * obs-vst: Update submodule to pull in CMake changes
  * obs-browser: Update submodule to pull in CMake changes
  * CI: Add necessary build system changes for universal and M1 builds
  * CI: Update build scripts and Github actions workflow
  * UI: Update CMakeLists.txt for main OBS app
  * libobs: Update CMakeLists.txt for libobs and associated libraries
  * plugins: Update CMakeLists.txt for included plugins
  * obs-scripting: Update CMakeLists.txt for scripting modules
  * deps: Update CMakeLists.txt for dependencies
  * cmake: Add bundle support files for macOS and Windows
  * cmake: Update CMake finders and helper modules
  * UI: Fix audio ids not being stored properly
  * win-waspai: Tighten version check for RTWQ
  * UI: Add webp to dropfiles
  * mac-capture: Add vbcable to whitelist for loopback devices
  * UI: Fix handling of remove signal with projectors
  * obs-frontend-api: Add function to get frontend translated string
  * libobs-d3d11: Simplify duplicator formats
  * UI: Remove some globals in AAC bitrate population
  * UI: Fix deferred source properties not updating
  * UI: Rename visual update callback variable
  * UI: Add undo/redo to dropfiles
  * UI: Fix mixer hide toggle in studio mode
  * libobs-d3d11: Relax minimum Windows for flip model
  * libobs: Handle filter_texrender format mismatch
  * libobs/graphics: Add gs_texrender_get_format
  * deps/media-playback: New AVPacket pattern
  * UI: Display dock-relevant context menu on titlebar
  * UI: Disable replay save button when paused
  * libobs: Fix overflow subtracting unsigned numbers
  * UI: Add mulitiview layout options without program
  * obs-ffmpeg: add NVENC blacklist check for Linux
  * UI: resolve .url, .lnk shortcuts during drag-and-drop
  * UI: Add events for renaming profiles/collections
  * UI: Fix unorthodox macOS Dock icon behavior
  * UI: Avoid calling obs_source_update multiple times
  * decklink: Use ComPtr for variables
  * libobs: Add function to load private sources
  * UI: Use get_new_source_name instead of strprintf
  * UI: Fix duplicated source names in audio settings
  * UI: Change 'Last Log' to 'Previous Log' in order to disambiguate things
  * UI: Remove OBSSceneItem QDataStream
  * UI: Simplify multi-instance check
  * win-dshow: Fix hwdevice_ctx leak
  * virtualcam-module: Revert changes since 27.1.3 (for now)
  * virtualcam-module: Prevent placeholder memory leak
  * virtualcam-module: Only initialize placeholder once
  * libobs: Update version to 27.2.3
  * virtualcam-module: Fix incorrect correct res/fps
  * UI: Remove conflicting setlocale call
  * UI: Restore LC_NUMERIC to C locale on Mac/Linux
  * libobs: Update version to 27.2.2
  * obs-scripting: Make callback "removed" variable atomic
  * libobs/util: Use integer math for Windows timing
  * libobs: Clamp video timing for safety
  * obs-browser: Log CEF version *after* library is loaded on macOS
  * libobs/util: Fix rounding error with os_sleepto_ns()
  * virtualcam-module: Remove unnecessarily inlines
  * virtualcam-module: Stop thread on Stop call
  * UI: Additional product details
  * win-dshow: Fix wrong AVCodecContext free call
  * win-dshow: Add hardware decode status to log
  * UI: Fix rendering of spaces & tabs in Log Viewer
  * obs-browser: Update version to 2.17.14
  * UI: Disable downscale filter setting for same resolutions
  * UI: Make volume meter tweakable by stylesheet
  * UI: Use selective repaint on volume meter scale
  * UI: Move "Check For Updates" menu to app menu on macOS
  * rtmp-services: Update Brime Live ingests
  * UI: Add shortcuts for Copy/Paste Transform
  * decklink: Don't load modules if Decklink not found
  * linux-v4l2: scandir with alphasort on non-Linux
  * libobs/graphics: gs_query_dmabuf_* on FreeBSD too
  * UI: Refresh edit menu on item locked signal
  * win-dshow: Add hardware decode toggle
  * obs-ffmpeg: Update nv-codec-header files
  * UI: Fix performance issues with the Log Viewer
  * UI: Add OBSQTDisplay::OnMove()/OnDisplayChange()
  * libobs: Only resize display if dimensions change
  * linux-v4l2: Fix warnings in mjpeg
  * win-wasapi: Fall back to old code if RTWQ fails
  * win-dshow: Ensure thread is joinable before joining
  * CI: Update workflow to copy SOVERSION symlinks
  * libobs: Update version to 27.2.1
  * obs-outputs: Set a fixed size socket buffer on Windows 7
  * CI: Bump Windows CEF cache to fix reported version
  * CI: Bump Windows CEF cache for new OnAcceleratedPaint2
  * obs-browser: Add support for custom OBS CEF
  * UI: Use std::unique_ptr for ui variables
  * obs-browser: Fix texture recreating every frame
  * linux-v4l2: Use decoded MJPEG pixel format
  * UI: Log 'Hide OBS from capture' on startup & settings change
  * libobs: Adjust path for legacy browser source block
  * UI: Refresh edit menu on item select/deselect
  * CI: Ensure SOVERSION symlinks exist in created App Bundle
  * CI: Update main workflow file to use fixed obs-deps
  * win-wasapi: Only enable work queue on Windows 10+
  * obs-filters: Reduced GPU work for common LUT cases
  * obs-filters: Reduce 3D LUT calculations
  * obs-filters: Interpolate LUT in linear space
  * obs-filters: Update original.cube
  * obs-filters: Add effect files to VS solution
  * obs-ffmpeg: Force mpegts format & disable restart on activate for srt & rist
  * linux-capture: Fix for pipewire capture leaking texture handles
  * obs-browser: Fix issues with rendering on Linux/macOS
  * obs-browser: Fix rendering on non-windows
  * UI: Don't collapse preview in Filters splitter view
  * libobs: Map wayland keymap with MAP_PRIVATE
  * obs-browser: Fix sRGB rendering
  * obs-browser: Update version to 2.17.10
  * obs-browser: Acquire, copy, and release immediately
  * UI: Avoid emiting events 2 times when renaming a profile
  * libobs/util: Fix VS static analysis warnings
  * UI: Correctly style "Chrome OS"
  * obs-ffmpeg: Split file by PTS instead of DTS
  * obs-ffmpeg, UI: Reset timestamps at splitting file
  * UI: Add automatic file splitting
  * obs-ffmpeg: Split ffmpeg_muxer output file by size or time
  * obs-ffmpeg: separate generate_filename function
* Tue Mar 29 2022 Jimmy Berry <jimmy@boombatower.com>
- Switch to https:// instead of git:// since no longer available.
* Tue Mar 29 2022 jimmy@boombatower.com
- Update to version 27.2.4:
  * libobs: Update version to 27.2.4
  * UI: Add missing previousIcon in Rachni theme
  * CI: Enable legacy CI for PRs to release branches
  * CI: Fix CEF zip extraction path on Windows
  * CI: Fix Qt XML Validator workflow
  * obs-libfdk: Set bitstream to ADTS for mpegts output
  * win-waspai: Tighten version check for RTWQ
  * mac-capture: Add vbcable to whitelist for loopback devices
  * UI: Fix handling of remove signal with projectors
  * UI: Fix deferred source properties not updating
* Thu Mar  3 2022 jimmy@boombatower.com
- Update to version 27.2.3:
  * virtualcam-module: Revert changes since 27.1.3 (for now)
  * virtualcam-module: Prevent placeholder memory leak
  * virtualcam-module: Only initialize placeholder once
  * libobs: Update version to 27.2.3
  * virtualcam-module: Fix incorrect correct res/fps
  * UI: Remove conflicting setlocale call
  * UI: Restore LC_NUMERIC to C locale on Mac/Linux
  * libobs: Update version to 27.2.2
  * virtualcam-module: Remove unnecessarily inlines
  * virtualcam-module: Stop thread on Stop call
  * win-dshow: Ensure thread is joinable before joining
  * obs-scripting: Make callback "removed" variable atomic
  * libobs/util: Use integer math for Windows timing
  * libobs: Clamp video timing for safety
  * libobs/util: Fix rounding error with os_sleepto_ns()
  * UI: Additional product details
  * linux-v4l2: scandir with alphasort on non-Linux
  * libobs/graphics: gs_query_dmabuf_* on FreeBSD too
  * UI: Refresh edit menu on item locked signal
  * linux-v4l2: Fix warnings in mjpeg
  * win-wasapi: Fall back to old code if RTWQ fails
  * CI: Update workflow to copy SOVERSION symlinks
  * libobs: Map wayland keymap with MAP_PRIVATE
* Tue Feb 22 2022 Jimmy Berry <jimmy@boombatower.com>
- Add new build dependencies:
  * pciutils-devel
  * pipewire-devel
- Condition pipewire support for Tumbleweed only as cmake does not find.
- Package additional icon sizes.
* Tue Feb 22 2022 jimmy@boombatower.com
- Update to version 27.2.1:
  * libobs: Update version to 27.2.1
  * obs-outputs: Set a fixed size socket buffer on Windows 7
  * CI: Bump Windows CEF cache to fix reported version
  * CI: Bump Windows CEF cache for new OnAcceleratedPaint2
  * obs-browser: Add support for custom OBS CEF
  * obs-browser: Fix texture recreating every frame
  * obs-browser: Fix issues with rendering on Linux/macOS
  * linux-v4l2: Use decoded MJPEG pixel format
  * UI: Log 'Hide OBS from capture' on startup & settings change
  * libobs: Adjust path for legacy browser source block
  * UI: Refresh edit menu on item select/deselect
  * CI: Ensure SOVERSION symlinks exist in created App Bundle
  * CI: Update main workflow file to use fixed obs-deps
  * win-wasapi: Only enable work queue on Windows 10+
  * obs-ffmpeg: Force mpegts format & disable restart on activate for srt & rist
  * linux-capture: Fix for pipewire capture leaking texture handles
  * UI: Don't collapse preview in Filters splitter view
  * obs-browser: Fix sRGB rendering
  * obs-browser: Update version to 2.17.10
  * obs-browser: Acquire, copy, and release immediately
  * rtmp-services: Update Picarto ingests
  * libobs: Update version to 27.2.0
  * Update translations from Crowdin
  * CI: Specify Windows Server 2019
  * UI: Fix uninitialized memory access in OBSPropertiesView
  * UI: Fix properties view crash with non-obs objects
  * UI: Add warning on startup for running in Wine
  * obs-ffmpeg: Fix svt-av1 rate control settings
  * Update translations from Crowdin
  * linux-capture: Fix missing parameter for pipewire capture
  * UI: Fix clang-format specifier
  * UI: Remove unnecessary call
  * UI: Fix filter props. getting recreated unnecessarily
  * UI: Don't create filter properties before splitter
  * UI: Improve properties view object safety
  * libobs: Add obs_object abstraction and functions
  * libobs: Rename OBSObj to OBSPtr
  * aja: Fix off-by-one output frame index calculation
  * rtmp-services: Update YouNow ingest
  * CI: Update Windows x86 obs-deps package to 2022-01-31
  * CI: Update Windows obs-deps package to 2022-01-31
  * CI: Update macOS obs-deps package to 2022-01-31
  * obs-transitions: Fix All Files option for Stingers
  * libobs: Add effect files to CMakeLists.txt
  * UI: Better Hide OBS Window description, add first time dialog & tooltip
  * libobs/graphics: Fix gs_get_format_bpp
  * UI: Properly close projector when source is removed (#5171)
  * vlc-video: Set channel limit to 8 instead of 2
  * rtmp-services: Update nanoStream Cloud / bintu ingests (#5884)
  * vlc-video: Enable surround sound support
  * win-dshow: Log buffered state
  * docs/sphinx: Add GS_RG16
  * libobs, libobs-d3d11, libobs-opengl: Add GS_RG16
  * win-dshow: Use OBS_SOURCE_FRAME_LINEAR_ALPHA
  * aja-output-ui: Fix crash when stopping AJA Preview output
  * obs-browser: Fix Windows crash if shared texture is unavailable
  * aja: Disable Analog In/Out selections in the UI
  * libobs: Free module if obs_module_load callback returns false
  * UI: Add separators to system tray context menu
  * UI: Fix unused variable warning on non-windows
  * aja: Fix Kona1 simultaneous capture/output
  * aja: Adjust whitespace for consistency
  * aja: Use SDI Transport selection to engage Auto detection
  * aja: Show/Hide SDI Transport/4K lists and options
  * aja: Fix 2xSDI UHD/4K YCbCr 2SI VPID lookup
  * aja: Hide duplicate HDMI IN entry for Kona HDMI
  * aja: Filter 6G/12G SDI Transport depending device/plugin type
  * aja: Disable UHD/4K high-framerate for Output
  * aja: Clear previous crosspoints when signal changes
  * aja: Remove unfinished 2x4K Squares support
  * aja: Re-work HDMI routing and add missing presets
  * aja: Fix HDMI RGB crosspoint indices
  * aja: Add framestore index helpers to Source/OutputProps
  * mac-vth264: Set RealTime property to False
  * mac-vth264: Use float for expected frame rate
  * mac-vth264: Remove OSX 10.8 compatibility code
  * UI: Show wait cursor while cleaning up scene data
  * flatpak: Update librist library
  * UI: Check current affinity before calling SetWindowDisplayAffinity
  * flatpak: Update libaom and SVT-AV1
  * obs-vst: Fix VSTs losing their settings when upgrading
  * flatpak: Enable communication with org.a11y.Bus
  * libobs: Respect push to talk/mute status in volmeter
  * obs-ffmpeg: Add MX450 to blacklist
  * docs/sphinx: Fix documentation for addref/release functions
  * UI: Disconnect group reorder signal
  * UI: Fix QLabel leak in OBSPropertiesView::AddProperty
  * UI: Fix transform options being wrongly enabled/disabled
  * libobs: Deprecate obs object addref functions
  * aja: Remove inter-plugin debug logging
  * UI: Fix bugtracker URL in AppData file (#5861)
  * libobs: Replace addref calls with get_ref
  * libobs: Use get_ref calls for obs.hpp helper classes
  * UI: Replace addref calls with get_ref
  * mac-syphon: Replace source addref calls with get_ref
  * image-source: Replace source addref calls with get_ref
  * libobs: Add obs_scene_get_ref()
  * UI: Allow 'Hide OBS window' on Windows 10 2004
  * UI: Fix Settings save crash on old Windows versions
  * obs-ffmpeg: Add new SVT presets
  * libobs: Prevent and log double destroy on sources
  * obs-browser: Suppress certain warnings
  * obs-vst: Fix formatting, fix size truncation warning
  * win-capture: Fix parameter mismatches
  * UI: Don't read unloaded module in source toolbar
  * libobs: Don't destroy mutex before destroying sources is done
  * obs-qsv11: Fix memory leak in QSV plugin module
  * UI: Add option to hide OBS windows on Windows
  * CI: Bump CEF caches to fix cookie crash bug
  * obs-vst: Fix closing & resizing VSTs on macOS
  * obs-vst: Fix mvMeter2 resize crash, fix SPAN resizing
  * aja: Fix UHD/4K YCbCr 3G Level-B 2SI preset
  * UI: Fix small typo
  * obs-browser: Update version to 2.17.8
  * UI: Optimize undo/redo functions with constant references
  * aja: Fix crash when capture thread is reset
  * aja: Workaround for SDI5 output not working on io4K+
  * obs-browser: Fix compilation on non-Windows
  * obs-browser: Update version to 2.17.7
  * libobs: Mark raw_active and gpu_encoder_active as volatile
  * win-capture: Don't list minimized UWP apps
  * UI: Use regexp to filter filename formatting
  * mac-vth264: Fix DTS timestamps when blank
  * win-capture: Use stack buffer for small window titles
  * win-capture: Make open_process_proc static
  * text-freetype2: Fix incorrect fread argument order
  * UI: Downgrade scalable logo on Linux to SVG 1.0
  * UI: Set desktopFileName for QApplication
  * UI: Fix memory leak in Auto-Configuration Wizard
  * libobs-opengl: Miscellaneous static analysis fixes
  * aja: Fix signal routing for 4xSDI UHD/4K RGB 3Gb
  * aja: Fix erroneous HDMI input selection for certain cards
  * aja: Rename IOSelection strings for HDMI and Analog
  * aja: Fix Kona1 not auto-detecting capture pixel format
  * media-playback: Fix rist demuxing
  * linux-v4l2: Fix timeout logging
  * libobs-d3d11: Fix formatting
  * libobs: Specify format string for bcrash
  * obs-filters: Fix incorrect format string
  * libobs-d3d11: Fix incorrect format string
  * libobs: Fix type mismatch on obs_property_text_monospace
  * UI: Log YouTube API HTTP request errors
  * aja: Fix Kona5/io4K+ 6G/12G-SDI routing and RGB HD-DualLink routing
  * aja: Fix for invalid default settings and empty cardID string
  * obs-vst: Fix crashes due to unhandled events, fix stutter when loading
  * UI: Remove unused 'Percent' string
  * obs-ffmpeg: Fix spelling mistake for 'Encoder.Timeout'
  * decklink-output-ui: Stop outputs on OBS_FRONTEND_EVENT_EXIT
  * libobs-opengl: Fix border color support on GL textures
  * libobs-d3d11: Log display nit range
  * obs-ffmpeg: Add missing "FFmpegOpts" locale
  * aja-output-ui: Add the Multi View UI options for new device.
  * aja: Fix format-security warning
  * UI: Fix crash when opening transition Properties dialog
  * obs-vst: Fix crashes when switching VSTs, and large channel counts
  * obs-browser: Update version to 2.17.6
  * libdshowcapture: Add P010 support
  * UI: Stop locking filter mutex while loading properties
  * libobs: Open a separate X11 connection for hotkeys
  * aja: Refactor, clean-up and fix bugs in the signal routing system, and add SDITransport UI option to assist signal routing.
  * obs-ffmpeg: Further FFmpeg deprecations fixes for FFmpeg 4.4+
  * UI: Fix push-to-talk/mute delay not saving
  * UI: Remove Apple deferred tray load
  * UI: Fix flash when starting minimized
  * UI: Fix hotkey JSON error for Advanced Replay Buffer
  * CI: Update Windows obs-deps package to 2022-01-01
  * CI: Update macOS obs-deps package to 2022-01-01
  * UI: Update context bar when exiting properties dialog
  * CI: Use GitHub mirror for PipeWire repository
  * UI: Disable WA_PaintOnScreen for projectors
  * linux-capture: Disable strict binding for NVIDIA drivers
  * UI: Ignore resizing item when it is locked
  * libobs-d3d11: Log display color space info
  * UI: Fix label offset on projector view
  * obs-vst: Fix resizing, always use source name in window title
  * UI: Don't recreate entire Hotkey Settings tab
  * UI: Fix taskbar icon visibility on light backgrounds
  * UI: Immediately apply tray icon change on Apply
  * flatpak: Use same commit hash for LuaJIT as macOS
  * obs-ffmpeg: Fix av1 encoding with fractional framerates
  * UI: Fix compile error in UpdateEditMenu from rebase
  * UI: Correctly enable edit menu items with multiple sources
  * UI: Reenable copy/paste transform
  * Revert "UI: Add checks for overwrite setting to replay buffer"
  * libobs: Stop all source processing on destroy
  * libobs: Call destroy signal after waiting
  * obs-browser: Update version to 2.17.5
  * UI: Fix "Null 'source' parameter" warning
  * UI: Do not localize timestamp in log file
  * UI: Correctly disable "Paste Duplicate" if required
  * UI: Add Rosetta Detection
  * UI: Remove unneeded include
  * docs: Fix frontend API docs for preview_scene functions
  * libobs: Remove all callbacks on source destroy
  * flatpak: Add SVT-AV1 support
  * flatpak: Add libaom support
  * flatpak: Add RIST support to FFmpeg
  * flatpak: Update FFmpeg to 4.4.1
  * Revert "libobs-opengl: Use PBO in device_stage_texture on macOS"
  * CI: Trigger multiplatform builds on release branches
  * UI: Increment showing in filters dialog
  * libobs: Move position for calling execute_graphics_tasks
  * UI: Fix vertical grayscale meters when volume is muted
  * libobs: Fix template errors on non-MS compilers
  * libobs, UI: Fix cpp auto-release assignment from OBSRefs
  * libobs-opengl: Use correct size for PIXELFORMATDESCRIPTOR
  * linux-capture: Standardize gs_color_format variable names
  * linux-capture: Unify format lookups
  * linux-capture: Move supported formats into a static table
  * linux-capture: Split array into two variables
  * linux-capture: Add preferred value out of the loop
  * linux-capture: Rename a variable
  * libobs-opengl: Swap order of out parameters
  * libobs-opengl: Remove unused function argument
  * CI: Split Flatpak beta and stable branches
  * CI: Trivial cleanup
  * UI: Fix build with YT integration without browser
  * obs-browser: Update version to 2.17.4
  * UI: Add `obs_frontend_open_source_interaction()`
  * docs: Fix names of filter/properties functions
  * UI: Fix Copy/Paste not including blend mode
  * UI: Remove unnecessary shared_ptr allocations
  * UI: Add alt-key support to Docks menu
  * obs-outputs: Only log SO_SNDBUF on RTMP socket
  * libobs, UI: Add support for beta builds
  * libobs: Check memory allocation in Windows crash handler
  * libobs: Use size_t for obs_encoder_get_frame_size
  * Revert "libobs, docs: Add function to get source version"
  * Revert "obs-filters: Remove duplicate color correction code"
  * Revert "obs-filters: Remove duplicate code from color key filter"
  * Revert "obs-filters: Remove duplicate code from chroma key filter"
  * obs-browser: Include `atomic` for browser source destroy
  * UI: Hold refs to existing sources during remove scene undo
  * UI: Hold refs to old sources during remove source undo
  * obs-vst: Fix race condition and prevent double invoke
  * obs-ffmpeg: Set frame_size for audio codec parameter
  * libobs: Add API to get encoder frame size
  * UI: Remove unneeded call when removing scene
  * UI: Add grayscale meters when volume is muted
  * UI: Display grayscale volume meter if muted
  * docs: Document obs_get_scene_by_name
  * UI: Filter out incompatible audio filters in A/V list
  * obs-browser: Correct set function names to match README
  * cmake: Add libRIST to copied Windows libs
  * flatpak: Deduplicate CEF from the bundle
  * flatpak: Add AJA NTV2 library
  * linux-capture: Fix Ubuntu 21.10 builds
  * linux-capture: Add fallback for PipeWire < 0.3.40
  * linux-pipewire: Handle DMA-BUF import failure
  * CI: Add PipeWire 0.3.40 to Flatpak
  * linux-capture: Announce supported modifiers via PipeWire
  * linux-capture: Bump minimal PipeWire version to 0.3.33
  * libobs-opengl: Implement DMA-BUF query functions for EGL renderer
  * libobs/graphics: Add Linux-only gs_query_dmabuf_* functions
  * linux-pipewire: Use DRM fourcc defines directly
  * libobs: Rename obs_audio_monitoring_supported to _available
  * CI: Update CEF hash for Flatpak to Release 4638
  * CI: Use Windows obs-deps release
  * libobs: Fix destruction order for destruction task queue
  * obs-outputs: Add support for "RTMP Go Away" feature
  * obs-outputs/librtmp: Add custom connect data callback
  * obs-outputs: Add support for reading RTMP packets
  * Revert "CI: Update CEF hash for Flatpak to fix crash"
  * libobs-d3d11: DuplicateOutput1 for DXGI capture
  * UI: Invoke QCoreApplication::quit in queued connection
  * UI: Use sendPostedEvents with deleteLater events on destroy
  * UI: Use null with sendPostedEvents()
  * obs-browser: Do not wait for browser on source destroy
  * Revert "mac-capture: Improve window capture performance"
  * libobs: Implement additional source blending modes
  * libobs: Expose blending operation types
  * mac-capture: Improve window capture performance
  * CI: Update CEF hash for Flatpak to fix crash
  * libobs: Implement deferred destruction of sources
  * libobs: Add obs_in_task_thread() function
  * libobs: Add ability to queue audio task
  * UI: Process deleteLater() tasks in OBSBasic::ClearSceneData
  * libobs/util: Add task queue helper
  * Revert "libobs: Do not release while traversing sources for tick"
  * libobs: Hold source ref during `source_remove` signal
  * CI: Fix build issues introduced by updates obs-deps
  * obs-vst: Avoid using empty editorWidget for deleteLater()
  * win-virtualcam: Make sure virtualcam output thread safe
  * libobs: Add preprocessor directive for AutoRelease types
  * CI: Update Windows CEF version to 4638 (Chromium 95)
  * CI: Update Linux CEF version to 4638 (Chromium 95)
  * CI: Update macOS CEF version to 4638 (Chromium 95)
  * UI: Update the filters window to be resizeable
  * UI: Add checks for overwrite setting to replay buffer
  * obs-outputs: Reset dbr bitrate before end_data_capture_thread start
  * UI: Add undo/redo for "Add existing source"
  * UI: Remove Qt Windows Extras for Qt 6 and later
  * Update translations from Crowdin
  * win-capture: Should not init module if HWND is invisible
  * UI: Fix a stack overlow caused by using OBSScene
  * libobs: Add Wayland hotkey infrastructure
  * libobs: Fix Numpad Minus naming in UI
  * libobs: Do not release while traversing sources for tick
  * CI: Update Crowdin Sync workflow to 0.1.2
  * libobs: Fix potentially unsafe linked list traversal
  * obs-browser: Fix deadlock
  * UI: More user-friendly error when using a bad output path
  * CI: Run Flatpak jobs on release branches too
  * libobs-opengl: Ensure proper draw buffer
  * Update translations from Crowdin
  * obs-browser: Fix build issues on Qt 5.9 (Ubuntu 18.04)
  * obs-browser: Update version to 2.17.1
  * obs-vst: Update submodule with a variety of bugfixes
  * libdshowcapture: Add FindPin, RGB24, & use CMake instead of pragma
  * linux-capture: Fix capturing on software rasterization setups
  * obs-ffmpeg: Set DRI devices and their name persistently
  * vlc-video: Emit media ended signal regardless of loop setting
  * linux-capture: Deinit pipewire only if we init'ed
  * UI: Add UUID to Twitch panel URLs
  * rtmp-services: Add Fantasy.Club
  * docs: add missing source output flags
  * libobs/util: Fix end_pos when pushing empty circlebuf front
  * UI: Set donation, bugtracker, and translate AppData fields
  * libobs: Disable function attributes for SWIG
  * UI/updater: Explicitly set PSAPI_VERSION=2
  * libobs: Add OBS_NORETURN and use it for crash handler
  * libobs: Add source cap to hint not to show properties
  * UI: Don't show properties on creation if no properties
  * aja: .rc file for the aja plugin
  * UI: Remove duplicate translate_button macro call
  * aja: Fix crash in output settings when no card present
  * aja: Disable plugin if no devices are found
  * CI: Add obsdeps to dylibBundler search
  * libobs: Fix missing return when loading non-OBS DLL
  * CI: Add extra rpath for macOS test binaries
  * CI: Bump WINDOWS_DEPS_CACHE_VERSION
  * CI: Update macos deps to 2021-12-05
  * aja: Static analysis bug fixes
  * CI: Increase Crowdin Sync Checkout Fetch Depth
  * CI: Update Crowdin Sync workflow to 0.1.1
  * CI: Don't publish betas to Flathub stable
  * text-freetype2: Fix unused parameter warning
  * obs-filters: Fix unused parameter warnings with speex disabled
  * UI: Fix unused lambda capture warning
  * UI: Uniquely identify Custom Browser Docks
  * UI: Fix service integration with older Qt versions
  * UI: Pass parent QWidget to Browser Docks
  * UI/importers: Automatically detect SL Collections on macOS
  * obs-ffmpeg: Fix memory leaks if replay buffer failed
  * linux-capture: Fallback on older PipeWire versions to SHM
  * linux-capture: Query used PipeWire versions
  * libobs: Fix add/remove of raw audio callbacks
  * obs-browser: Update to 2.17.0, add CEF 4638 support
  * UI: Add kudos to AppData file
  * frontend-tools: Cleanup libobs C++ type use
  * UI: Cleanup libobs C++ type use
  * libobs: Add AutoRelease OBSRef wrappers for OBS types
  * UI: Add separator before Custom Browser Docks in Dock menu
  * UI: Remove unused/nonexistent signal/slot connections
  * UI: Move Docks into top level menu
  * CI: Allow Flatpak audio plugins be found
  * CI: Add extension point to Flatpak plugins
  * CI: Update Flatpak's v4l-utils to 1.22
  * CI: Update Flatpak's x264
  * CI: Add Crowdin Synchronization
  * UI: Add missing Interact tooltip in compact source toolbar
  * UI: Expose cURL error if Remote Text error text is empty
  * UI: Minimize context bar when too small
  * CI: Drop "(Experimental)" from the Flatpak workflow
  * CI: Publish releases on Flathub
  * CI: Use version 4 of the flatpak-builder action
  * CI: Trivial job renaming
  * CI: Make YAMLint happy
  * .gitignore: Add flatpak-builder folders
  * CI: Update XML/clang-format validation job names
  * linux-capture: Implement stream restoration
  * linux-capture: Add getter to screencast portal version
  * UI: Install correct logos
  * libobs: Add raw audio callback function
  * UI: Add option for only one fullscreen projector per screen
  * UI: Set Twitch Panel Dark Mode using OBS theme
  * libobs: Free async cache when sources output NULL frames
  * UI: Fix bug with audio balance slider not updating
  * UI: Fix context bar shutdown crash
  * UI: Recreate nested scenes on scene delete undo
  * libobs: Add obs_scene_prune_sources
  * docs: Add missing frontend-api calls + organize
  * docs: Add missing config_t get/set functions
  * docs: Add missing obs_source_t functions + organize
  * docs: Minor function description tweaks (reference-scenes)
  * UI: Use std::gcd for aspect ratio
  * libobs: Fix gs_texture_2d::BackupTexture with GS_TEXTURE_CUBE
  * aja: Capture and Output plugin for AJA Video Systems IO devices
  * obs-ffmpeg: Properly name FFmpeg lib used
  * obs-ffmpeg: Fix NVENC old codec naming removed in FFmpeg
  * obs-ffmpeg: Respect AVFormatContext and AVOutputFormat constness
  * CONTRIBUTING.rst: Add service submission guidelines (#5562)
  * obs-ffmpeg: Include channel_layout.h
  * obs-ffmpeg: Include avcodec header for AVCodecContext
  * win-dshow: Use AVFrame.pts instead of AVFrame pkt_pts
  * ipc-util: Fix potential ready_event hang
  * UI: Delete OBSDisplay on window hide on unix
  * inject-helper: Remove UNUSED_PARAMETER macro
  * text-freetype2: Move default settings to .get_defaults
  * UI: Update adv audio props on monitoring type change
  * libobs: Add `audio_monitoring` source signal
  * libobs/UI: Stop using preprocessor directives for monitor
  * libobs: Add obs_audio_monitoring_supported()
  * UI: Remove unnecessary calls to `RefreshSources()`
  * UI: Refresh source tree when an item source is removed
  * UI: Import Streamlabs Screen Capture source type
  * libobs, libobs-d3d11: Add support for NT Handle shared textures
  * docs: Document obs_group_or_scene_from_source
  * docs: Fix outdated speaker_layout enum
  * obs-frontend-api: Add scripting shutdown event
  * docs: Add obs_frontend_get_current_record_output_path()
  * UI: Add obs_frontend_get_current_record_output_path()
  * UI: Update python linkage for older compilers
  * rtmp-services: Add Manyvids.com
  * obs-qsv11: Remove Intel discrete device ID checking
  * Revert "libobs: Avoid recycling async frames"
  * UI: Link python when obs-scripting python is enabled
  * linux-v4l2: Change search strategy for v4l2loopback devices
  * UI: Apply transforms/crops correctly to sources on paste
  * obs-transitions: Fix stinger transition looping
  * rtmp-services: add PhoneLivestreaming
  * UI: Add undo/redo for resetting filters properties
  * docs: Add `_CHANGING` frontend events
  * UI: Add `_CHANGING` frontend events
  * UI: Update Edit Transform dialog on scene switch
  * rtmp-services: Add Autistici.org
  * rtmp-services: add Utreon
  * libobs: Add obs_get_transition_by_name
  * UI: Don't load existing sources for scene removal undo
  * UI: Add undo/redo for context bar text changes
  * obs-ffmpeg: Fix starting video packet offset in replay-buffer
  * pulse: fill audio monitor buffer more aggressively
  * rtmp-services: add Kuaishou live
  * UI, libobs, obs-plugins: Fix compiler warnings
  * UI: Set correct text in system tray on startup
  * UI: Remove duplicated StreamingActive() function
  * UI: Match Windows taskbar state to tray icon
  * CI: Enable services on Flatpak builds
  * CI: Fix error when uninstalling curl and php
  * UI: Focus correct filter list when opening filter view
  * UI: Focus filter list when adding new filter
  * linux-capture: Sort windows by name
  * libobs-opengl: Use PBO in device_stage_texture on macOS
  * linux-v4l2: Support for Motion-JPEG codec
  * obs-qsv11: Fix memory leaks
  * rtmp-services: update CamSoda domains
  * obs-ffmpeg-mux: Add support for rist protocol
  * obs-filters: Remove duplicate code from chroma key filter
  * obs-filters: Remove duplicate code from color key filter
  * obs-filters: Remove duplicate color correction code
  * libobs, docs: Add function to get source version
  * UI: Migrate to Helix Twitch API
  * obs-ffmpeg: Add AOM AV1 and SVT-AV1 encoders
  * obs-ffmpeg/ffmpeg-mux: Allow codecs of any type
  * libobs: Allow last encoder error for last output error
  * obs-x264: Move options parser to its own lib
  * UI: Add Hotkey filter search and duplicate detection
  * CI: Add copyright information to macOS bundle plist
  * simde: Update README.libobs
  * simde: Don't format simde
  * Themes: Specify QListView instead of QListWidget
  * obs-qsv11: Add ENABLE_QSV11 option
  * UI: Disable properties for groups in context menu
  * obs-filters: Add libSpeexDSP guard to method
  * UI: Fix vertical/horizontal scene item alignment
  * libobs: Mark unused audio functions as deprecated
  * Revert "libobs: Remove unused volmeter code"
  * libobs: Remove unused volmeter code
  * UI: Remove duplicate minimum width definition
  * rtmp-services: add "Jio Games"
  * CI: Validate Qt XML in UI files
  * UI: Clean up XML warnings in layout files
  * UI: Add Qt XML Schema definitions for validation
  * obs-qsv11: Add plain-text copy of QSV11 email chain
  * obs-qsv11: Remove Intel NDA from qsv11 plugin
  * COPYING: Use license file from gnu.org
  * mac-virtualcam: Remove unnecessary plugin version number
  * UI: Cleanup advanced audio functions
  * UI: Refactor Frontend API and header
  * UI: Change position of filters defaults button
  * UI: Make transition duration suffixes consistent
  * obs-ffmpeg: Fix unwritten audio-only output
  * libobs/audio-monitoring: Fix PulseAudio monitoring volume for u8 format
  * libobs/audio-monitoring: Fix PulseAudio monitoring volume for s32 format
  * decklink-captions: Build with Windows file descriptor
  * UI: Fix build with Clang and libc++
  * CI: Update KDE image to 5.15-21.08 (Flatpak)
  * CI: Update modules for Flatpak build
  * CI: Update KDE Platform to 5.15-21.08 (Flatpak)
  * UI: Translate to current OS for all colection imports
  * UI: Resolve relative paths on scene collection import
  * UI: Use correct color property for freetype in toolbar
  * UI: Make toolbar color selectors respect alpha
  * mac-virtualcam: Remove unneeded includes
  * v4l2: Ignore menu controls with no permissible values
  * UI: Don't save defaults in oldSettings in properties
  * UI: Disable paste source menu items when removed
  * UI: Don't copy via name, use weak refs
  * libobs: Add obs_weak_source_expired()
  * obs-scripting: add transition duration functions
  * UI: Update Edit menu item states before displaying
  * libobs/callback: Make proc_handler_t threadsafe
  * UI: Fix broadcast button state for autostart without autostop
  * UI: Show warning if starting/stopping broadcast fails
  * UI: Fix YT broadcast start/stop failing due to redundant transition/reset
  * UI: Fix formatting with both 12.0.0 and 12.0.1
  * UI: Fix formatting for clang-format 12.0.0 (I guess)
  * UI: Fix formatting with clang-format 12
  * CI: Update clang-format from 10 to 12
  * clang-format: Commit file changes for clang-format 12
  * clang-format: Commit file changes for clang-format 11
  * UI: Add new vector-based menubar icons for macOS
  * win-wasapi: Log settings
  * win-wasapi Improve default device handling
  * win-wasapi: Schedule work on real-time work queue
  * UI: Add support for real-time work queue
  * win-wasapi: Register capture thread with MMCSS
  * win-wasapi: Remove bools and persist threads
  * win-wasapi: Clean reset on initialization failure
  * win-wasapi: Remove unnecessary inline tags
  * win-wasapi: Remove undefined function InitName
  * win-wasapi: Rename InitRender to ClearBuffer
  * win-wasapi: Simplify sample rate logging
  * win-wasapi: Remove persistent references
  * win-wasapi: Persist objects beyond Start/Stop
  * win-wasapi: Make InitDevice throw to log errors
  * win-wasapi: Fix incorrect log strings
  * win-wasapi: Mark GetWASAPIAudioDevices_ as static
  * libobs/audio-monitoring: Add reconnect logic
  * libobs/audio-monitoring: Move variable assignment
  * libobs/audio-monitoring: Add WASAPI init helper
  * libobs/audio-monitoring: Remove unnecessary device
  * libobs/audio-monitoring: Fix mutex leak
  * win-wasapi: Remove monitor invalidation code
  * libobs/media-io: Register audio thread with MMCSS
  * libobs/util: Improve os_sleepto_ns on Windows
  * obs-outputs: Remove unnecessary header
  * obs-outputs: Remove WIN32_LEAN_AND_MEAN define
  * libobs: Remove WIN32_LEAN_AND_MEAN
  * UI: Tuck variable inside macro guard
  * UI: Remove NOMINMAX from CMake scripts
  * UI: Use patterns that avoid std::min/max
  * coreaudio-encoder: Remove NO_MIN_MAX
  * libobs/util: Simplify emmintrin.h wrapper macro
  * libobs/graphics: Fix vec2 min/max functions
  * obs-text: Update header for ARM64 compile
  * decklink: Make header self-sufficient
  * libobs, libobs-opengl: Consistent near/far undef
  * UI: Improve installer, add release notes & Quickstart link
  * vlc-video: Improve logging with prefix & VLC version
  * UI: Log compiled & runtime Qt versions
  * win-capture: Use DPI context for game capture
  * win-capture: Use DPI context for window BitBlt
  * cmake: Don't link with PulseAudio when disabled
  * UI: Add restart message on profile change
  * UI: Add ShutDownActiveOutputsOnExit setting
  * libobs: Clear unused pointers for obs_source_output_audio()
* Tue Oct  5 2021 Jimmy Berry <jimmy@boombatower.com>
- Update to version 27.1.3:
  * libobs: Update version to 27.1.2
  * Revert "libobs: Don't return/set 0 mixers for non-audio sources"
  * libobs: Update to version 27.1.2
  * Revert "UI: Disable hotkeys when a user is expected to type text"
  * libobs: Don't return/set 0 mixers for non-audio sources
  * UI: Fix tab stop order for Draw safe areas
  * UI: Do not disable AutoConf bandwidth test for YouTube
  * libobs: Remove DrawSrgbDecompressPremultiplied
  * UI: Fix Twitch bandwidth test checkbox
  * UI: Remove thread from YouTube auto config
  * obs-browser: Filter textures in linear space
  * UI: Adjust minimum size of source toolbars smaller
  * libobs/util: Add type test in darray macros for GCC
  * libobs/util: Add a cast for da_push_back_array argument
  * libobs: Fix const qualifier mismatch on DARRAY
  * libobs: Add casts to da_push_back_array arguments
  * libobs: DrawSrgbDecompress for default_rect.effect
  * libobs: Simplify util_mul_div64 for x64 on Windows
  * win-capture: Update graphics hook version to 1.7.1
  * libobs: Update version to 27.1.1
  * UI: Add missing Auth::Load() when duplicating/creating profile
  * linux-capture: Fail when libdrm missing
  * obs-browser: Update translations from Crowdin
  * obs-browser: Update version to 2.16.2
  * Update translations from Crowdin
  * libobs: Update version to 27.1.0
  * linux-capture: Add libdrm dependency check (#5326)
  * Revert "UI: Update volume controls by callback"
  * libobs: Make portal inhibitor asynchronous
  * UI: Prevent Restream OAuth disconnection
  * linux-capture: Omit implicit modifier token when creating texture
  * libobs-opengl: Load EGL via Glad on Wayland platform
  * docs: Add transition duration changed event
  * win-dshow: Don't buffer Elgato Facecam device by default
  * UI: Fix enter/esc when hotkeys are disabled in focus
  * linux-capture: Lookup session handle without typechecks
  * CI: Fix double zip by uploading build folders
  * UI: Use STL random as fallback
  * UI: Fix AuthListener error HTTP response body
  * UI: Abort YouTube login on cancel or listener fail
  * UI: Force minimum reconnect delay of 1 second
  * UI: Remove test YouTube QSS from Dark theme
  * libobs-d3d11: Fix present skip comment
  * UI: Add label/widget buddying to YouTube dialog
  * UI: Use secure RNG for generating YouTube state parameter
  * UI: Properly verify state parameter for YouTube auth
  * libobs-d3d11: Use waitable object to avoid stalls
  * libobs-d3d11: Simplify DXGI factory creation
  * libobs-d3d11: Prefer ComPtr Clear() over Release()
  * libobs: Support move for mismatched ComPtr
  * UI: Update Acri theme styling
  * UI: Update dark theme button styling
  * UI: Fix loading auto start/stop setting in YT dialog
  * cmake: Add Qt JPEG/GIF plugins to Windows libraries
  * UI: Add thumbnail option to YouTube broadcast setup
  * UI: Add postDataSize option to GetRemoteText
  * UI: Fix used source for SetCurrentScene during undo
  * UI: Remove unused RemoveSelectedSceneItem slot
  * libobs: Block sceneitem create if item source is removed
  * UI/updater: Remove dependency on psapi.lib
  * win-capture: Remove dependency on psapi.lib
  * libobs: Remove dependency on psapi.lib
  * UI: Check selected broadcast when re-opening YT dialog
  * UI: Change YouTube Broadcast Dialog title
  * UI: Add remember settings checkbox to YT broadcast setup
  * UI: Rework YouTube broadcast setup flow
  * deps/media-playback: Handle discontinuities to fix video stalls
  * libobs: Actually fix ungroup deadlock
  * Revert "libobs: Avoid request graphics lock after full_lock(scene)."
  * libobs: Restrict emmintrin.h to x86(_64) platform
  * UI: Add -DNOMINMAX to CMake on MSVC
  * libobs: Fix near and far redefinition on MSVC
  * libobs: Fix connect() redefinition on MSVC
  * obs-outputs: Add WIN32_LEAN_AND_MEAN to avoid symbol clash
  * libobs: Avoid request graphics lock after full_lock(scene).
  * libobs: Add profiler section for send_packet
  * libobs-winrt: Require Windows 10 SDK 20348
  * cmake: Require Windows 10 SDK 20348
  * libobs-d3d11: Use ALLOW_TEARING if supported
  * libobs-d3d11: Use FLIP_DISCARD on Windows 11
  * libobs/util: Const-correct win_version_compare
  * UI: Disable reconnect for bandwidth test
  * UI: Enable AutoConfig bandwidth test for YT integration
  * UI: Fix Qt6-incompatible operator usage
  * UI: Fix Qt6-incompatible call to QLocale::setDefault
  * UI: Update volume controls by callback
  * rtmp-services: Add Disciple Media
  * libobs: FIx missing noexcept warnings
  * libobs/graphics: Fix gs_generalize_format warning
  * UI: Fix YT chat being shown when selecting private event
  * UI: Only start YT check thread if auto-start is disabled
  * UI: Disable hotkeys when a user is expected to type text
  * UI: Remove obsolete/unused struct members
  * UI: Restore auth reset when switching services
  * UI: Remove unused struct
  * UI: Fix vertical stretching in audio settings pane
  * obs-outputs: Disable Windows socket loop when using RTMPS
  * UI: Use OBS locale for YouTube categories API
  * libobs/util: Improve SetThreadDescription usage
  * UI: Fix missing broadcast state reset on force-stop
  * UI: Start YouTube check thread after output starts
  * UI: Actually set AutoConfig bitrate max to 51 Mbps
  * UI: Change YouTube description input to QPlainTextEdit
  * UI: Bump AutoConfig bitrate maximum to 51 Mbps
  * UI: Add missing properties to ResetBroadcast
  * UI: Fix crash when output source 0 is null
  * win-capture: Clear stale pointers for game capture
  * libobs/util: Remove old ifdefs
  * UI: Fix disabled auto-start/stop checkboxes
  * rtmp-services: Remove 17LIVE
  * UI: Update png to svg in ui files
  * docs: Clarify only DMA-BUFs with a single modifier are supported
  * pipewire: Create textures from multiplanar DMA-BUF
  * UI: Remove "Fullscreen Interface" menu on macOS
  * UI: Fix source toolbar shifting when nothing is selected
  * UI: Adjust minimum size of source toolbars
  * UI: Allow overriding keyframe interval if smaller
  * UI: Cache YouTube channel name
  * libobs: Add missing util.hpp to CMakeLists.txt
  * obs-filters: Fix NvAFX mutex leak
  * libobs: Fix pthread mutex leaks
  * libobs/util: Fix pthread mutex leaks
  * libobs/media-io: Fix leaks and error handling
  * libobs/callback: Fix pthread mutex leaks
  * deps/obs-scripting: Fix pthread mutex leaks
  * libobs/util: pthread_mutex_init_recursive helper
  * UI: Adjustments to YouTube integration strings
  * obs-browser: Disable Qt tooltip on old Qt versions
  * obs-browser: Update version to 2.16.0
  * UI: Add YouTube Chat Dock
  * libobs: Defer reconfiguring encoders to the encode threads
  * Revert "obs-ffmpeg, obs-qsv11: Disable dynamic bitrate support"
  * UI: Fix incorrect OBSTheme definition for highlighted text color
  * UI: Use Palette in all default themes
  * UI: Load theme palette before loading theme
  * image-source: Fix gif not working in studio mode
  * UI: Add styling for YouTube integration
  * cmake: Copy correct file for Qt imageformat plugin
  * UI: Use inline const for shared vector
  * decklink: Cleanup hide/show code
  * UI: Hide auto-start/auto-stop options in YouTube dialog
  * UI: Replace bad YouTube link with popup helper
  * decklink: Fix deactivate when not showing
  * UI: Fix minor leak
  * UI: Add option to draw safe areas in preview
  * obs-ffmpeg, obs-qsv11: Disable dynamic bitrate support
  * UI: Add required links when using YouTube
  * libobs-winrt: Replace casts with data access
  * libobs-winrt: Improve error logging code
  * decklink-output-ui: Don't update UI during shutdown
  * win-dshow: Avoid redundant string conversions
  * win-dshow: Use constant references for resolution check
  * UI: Fix redo recreating sources in the wrong scene
  * UI: Show source icon in context bar
  * UI: Add menu bar item to show missing files dialog
  * UI: Fix missing #if for autostart warning
  * UI: Add "Don't show again" checkbox to YT auto start warning
  * UI: Show loading indicator while fetching YouTube Events
  * UI: Fix YouTube event selection, API usage, stream resumption
  * UI: Improve YouTube (error) translatability
  * UI: Show error if Google account has no channels
  * UI: Improve YouTube API HTTP error handling
  * UI: Add fail_on_error parameter to GetRemoteFile
  * win-capture: Fix D3D12 third party overlay capture
  * UI: Dim hidden source items in source tree
  * mac-virtualcam: Move DAL plugin to plugin data directory
  * Revert "UI: Remove macOS-Default Full Screen Menu Item"
  * UI: Remove macOS-Default Full Screen Menu Item
  * UI: Show name of scene item in Transform window title
  * UI: Fix media controls toolbar default size and styling
  * UI: Change the Source Toolbar to not be fixed size
  * UI: Change QWidgets to QFrame so Qt Creator doesn't hide these entries
  * UI: Apply QSS to generic hotkey settings label
  * cmake: Remove local files for checking threading support
  * UI: Clean up Update form markup
  * UI: Clean up Remux form markup
  * UI: Clean up Missing Files form markup
  * UI: Clean up Importer form markup
  * UI: Clean up Custom Browser Docks form markup
  * UI: Clean up Transform form markup
  * UI: Clean up Interact form markup
  * UI: Clean up Filters form markup
  * UI: Clean up About form markup
  * UI: Clean up AutoConfig form markup
  * UI: Clean up toolbar form markup
  * UI: Clean up Settings form markup
  * UI: Query rtmp-services for stream key link URLs
  * rtmp-services: Add stream key link URLs
  * rtmp-services: Change "stream key link" key to "stream_key_link"
  * UI,obs-transitions: Enable missing files dialog for stinger transition
  * rtmp-services: Add BoxCast
  * Revert "mac-virtualcam: Move DAL plugin to plugin data directory"
  * mac-virtualcam: Move DAL plugin to plugin data directory
  * graphics-hook: Fix D3D11On12 usages
  * deps/media-playback: Fix trailing whitespace
  * UI: Fix compiler error
  * UI: Fix frontend API cleanup/exit event order
  * deps/media-playback: Fix bug about audio without best_effort_timestamp
  * frontend-tools: Fix crash on shutdown
  * UI: Create YouTube LiveStream objects as non-reusable
  * UI: Force Wayland usage under Wayland session
  * obs-outputs: Fix binding to IPv6 addresses on *nix
  * linux-capture: Load XSHM capture on EGL/X11
  * deps/media-playback: Less accurate sleep
  * libobs-d3d11: Avoid vector usage
  * libobs: Avoid recycling async frames
  * libobs/graphics: Avoid darray recycle
  * UI: Trim custom server string
  * UI: Add functions to open properties and filters
  * obs-frontend-api: Send OBS_FRONTEND_EVENT_SCENE_COLLECTION_CLEANUP
  * obs-transitions: Fix desync of stinger track matte
  * rtmp-services: Fix comparison mismatch warning
  * UI: Fix unused variable outside of #if
  * rtmp-services: Fix typo'd "recommended" key for various services
  * Revert "UI: Initialize Studio mode after loading scenes"
  * rtmp-services: Add 17LIVE service
  * rtmp-services: Add Volume.com
  * libobs/util: Fix reading memory usage on Linux
  * obs-transitions: Add "Mask only" track matte option
  * obs-transitions: Fix missing newline at end of file
  * UI: Replace '&&' with 'and' in YT integration
  * UI: Show autoremux progress bar
  * UI: Autoremux Replay Buffer
  * Revert "docs: Rename Code of Conduct to fix GitHub detection"
  * docs: Rename Code of Conduct to fix GitHub detection
  * UI: Add YouTube integration
  * docs: Add link to CoC to contributing guidelines
  * obs-filters: Correct log prefix for noise suppression filter
  * obs-filters: Use correct NVIDIA capitalization
  * UI: Fix da_push_back taking a wrong type of item
  * libobs: Fix da_push_back taking a wrong type of item
  * rtmp-services: Add "Lovecast"
  * UI: Fix undo delete scene that is used as source
  * Add Code of Conduct
  * obs-ffmpeg: Translate VAAPI property names
  * obs-filters: Sample mask/blend texture linearly
  * Revert "UI: Disable drag/drop on Linux scenes/sources (for now)"
  * obs-browser: Update version to 2.15.0
  * UI: Add support for external browser OAuth
  * UI: Specify exact service to auth login callbacks
  * UI: Add request type param to GetRemoteText
  * UI: Set Qt locale to current OBS locale
  * UI: Include QtNetwork as a direct dependency
  * win-capture: Fix formatting
  * obs-filters: Minor NVAFX cleanup
  * UI: Simplify expressions in GetMonitorName
  * win-capture: Use better defaults in thread_is_suspended
  * win-capture: Move NT functions to shared file
  * UI: Handle prefixes when using paths in recording format
  * libobs: Add stop_audio function, change shutdown order
  * UI: Initialize Studio mode after loading scenes
  * decklink: Add destructor for OBSVideoFrame, initialize flags
  * UI: Use larger buffer for scene collection filename
  * decklink: Fix truncation warnings
  * libobs: Round up chroma sizes for odd resolutions
  * libobs: Fix stack buffer overflow in build_current_order_info
  * UI: Fix ambiguous conversion error
  * UI: Fix formatting on window-basic-settings.cpp
  * UI: Add "18 Scenes" multiview option
  * flatpak: Remove D-Bus permissions to talk to session managers
  * libobs: Add portal inhibitor
  * decklink: Don't show incompatible formats
  * libobs-winrt, win-capture: Linear SRGB support
  * libobs-opengl: Fix GS_R10G10B10A2 format
  * libobs-d3d11: Relax texture format copy check
  * libobs-d3d11: Use typeless texture for duplicator
  * libobs: Plumb texcoord hint to reduce GPU cost
  * libobs: Add gs_generalize_format helper
  * libobs: Add DrawSrgbDecompress default technique
  * libobs: DrawSrgbDecompressPremultiplied technique
  * UI: Fix displayed autoremux file name
  * UI: Add obs-frontend-api functions to create/delete profiles
  * UI: Add startup flag to disable missing files window
  * UI: Add obs_frontend_get_current_profile_path()
  * libobs: Add `obs_enum_all_sources()`
  * libobs, UI: Add support for button properties as links
  * libobs/nix: List Flatpak search paths
  * rtmp-services: add bilibili live
  * pipewire: Properly pass sizes to gs_draw_sprite_subregion
  * obs-filters: Fix comparison type mismatch
  * obs-ffmpeg: Fix comparison type mismatch
  * libobs: Fix warnings
  * text-freetype2: Add alpha channel property
  * mac-syphon: Use DrawOpaque as necessary
  * libobs: Add DrawOpaque for rect effect
  * libobs: Fix memory overrun if libobs version mismatches
  * UI: Log Show/Hide transitions on scene collection load
  * cmake: Enable full optimizations for RelWithDebInfo MSVC builds
  * UI: Fix audio mixer UI not updating from threads
  * libobs/callback: Fix signal_handler_disconnect_global
  * rtmp-services: Fix implicit function declaration
  * rtmp-services: Update Facebook recommended settings
  * rtmp-services: Implement bitrate matrix
  * UI: Check if recording is paused when trying to pause
  * mac-capture: Update display names
  * linux-capture: Use portal's D-Bus on PipeWire captures
  * linux-capture: Add getters for portal's D-Bus connection and proxy
  * linux-capture: Conditionally register PipeWire captures
  * obs-qsv11: Update Intel Media SDK to 2021 R1
  * UI: Handle HTTP errors for fetching remote files
  * UI: Handle & log HTTP errors for RemoteTextThread
  * win-capture: Return early in property callbacks if param is null
  * win-capture: Check for WGC support on plugin load
  * win-capture: Determine D3D11 usage once per run
  * UI: Remove fractional scaling ifdefs
  * UI: Make projector display resolutions DPI-aware
  * libobs-winrt: Use better Windows SDK version check
  * obs-ffmpeg: Don't purge packets when there are none
  * pipewire: Properly account for cursor hotspot
  * UI: Fix win uninstall not deleting desktop shortcut
  * UI: Fix code indentation for Edit Undo/Redo
  * UI/installer: Silently install Visual C++ Redist
  * win-capture: Bump graphics hook version to 1.7.0
  * win-capture: Remove custom function hooking
  * graphics-hook: Use Detours for function hooking
  * graphics-hook: Remove unused header
  * UI: Delete log viewer when closing it
  * UI: Simplify log viewer on launch code
* Fri Jul 30 2021 Guillaume G. <guillaume@opensuse.org>
- Build on aarch64 as well
* Fri Jun 18 2021 Jimmy Berry <jimmy@boombatower.com>
- Rebase patches:
  - 0001-Prefix-modinfo-with-sbin-since-not-in-normal-path.patch
  - 0002-Include-moonjit.patch
- Add OBS packaged cef_binary_4280_linux64.tar.bz2.
- Include browser build cmake options.
- Add dependencies:
  - libqt5-qtbase-private-headers-devel
  - pipewire-devel
- Disabled browser build as needs more packaging work.
* Fri Jun 18 2021 jimmy@boombatower.com
- Update to version 27.0.1:
  * UI: Fix unused parameter warning
  * Update translations from Crowdin
  * libobs,deps/media-playback: Avoid bitfields
  * UI: Fix context bar crash
  * libobs: Update version to 27.0.1
  * UI: Handle mac-vth264 encoder ID change
  * UI: Optimize backup scene for undo/redo
  * obs-ffmpeg: Add missing return statement
  * UI: Fix filters changes not properly being added to undo stack
  * obs-ffmpeg: NVENC usage fixes
  * UI: Translate Undo action "Delete Scene" and include scene name
  * obs-ffmpeg: Support lack of Psycho Visual Tuning
  * UI: Don't execute or track empty SceneItem move actions
  * Revert "UI: Cleanup on_scenes_currentItemChanged function"
  * obs-ffmpeg: Add linear alpha setting
  * deps/media-playback: Plumb linear alpha flag
  * libobs: Plumb linear alpha flag
  * Revert "UI: Fix spamming of log when setting current scene"
  * CI: Bump dmgbuild to 1.5.2 to fix detach error
  * UI: Disable Copy Filters in scene list for scene with no filters
  * UI: Disable Copy Filters in Audio Mixer for source with no filters
  * obs-filters: Fix swapped chroma distance values
  * libobs: Assume sRGB instead of linear for 64 bpp
  * libobs: Restrict direct filtering to SRGB match
  * UI: Disable drag/drop on Linux scenes/sources (for now)
  * CI: Fix dmgbuild breaking CI by pinning its version number
  * libobs: Update version to 27.0.0
  * UI: Remove scene collection undo/redo actions
  * Update translations from Crowdin
  * obs-filters: Test if NVAFX is supported on load
  * UI: Fix OBS signal recursion
  * obs-transitions: Disable separate track matte file for now
  * UI: Correct add_action repeatable arg type
  * libobs: Straight alpha blend for filtered inputs
  * UI: Fix null string being passed to blog()
  * UI: Add Group/Ungroup Undo/Redo actions
  * UI: Do not allow new undo actions while undo disabled
  * UI: Add OBSBasic::BackupScene() with scene param
  * cmake: Fix Detours package name CMake warning
  * graphics-hook: Add Detours include dir
  * CI: Add check for code signing credentials used by notarization
  * win-capture: Remove D3D12 fix toggle
  * UI: Fix hide undo/redo not working with group items
  * libobs: Add obs_group_or_scene_from_source()
  * win-capture: Bump graphics hook version to 1.5.0
  * graphics-hook: Try multiple D3D12 queues
  * graphics-hook: Do not persist device unnecessarily
  * graphics-hook: More logging to help debugging
  * graphics-hook: Kill early return
  * graphics-hook: Give up on DXGI swap chain
  * graphics-hook: Reduce variable scopes
  * graphics-hook: Prevent recursive free
  * graphics-hook: Fix potential D3D12 device leak
  * graphics-hook: Use Detours for D3D12 hook
  * graphics-hook: Link Detours library
  * cmake: Add module for Detours
  * CI: Add versioning for dependencies zip file
  * obs-vst: Remove unused code
  * decklink-output-ui: Stop outputs when unloading
  * decklink-output-ui: Render texrender once per frame
  * UI: Add versioned sources to scene collection importer
  * UI: Fix scene collection importer OS translation
  * obs-transitions: Make sure gs calls are in graphics context
  * obs-filters: Fix blend state for Scale filter
  * obs-filters: Premultiply alpha for precision
  * libobs: Add srgb.h to CMakeLists.txt
  * obs-transitions: Fix memory leak
  * UI: Add paste source undo/redo actions
  * UI: Add disable push/pop to undo/redo stack
  * UI: Use "enabled" instead of "disabled" variable name
  * UI: Rename enable/disable funcs for undo/redo stack
  * cmake: Fix FindJack to support finding PipeWire's libjack
  * decklink: Fix crash during shutdown when output is on
  * obs-filters: Fix color key distance
  * libobs: Remove DrawAlphaBlend technique
  * image-source: Premultiply images on load
  * libobs: Support premultiplying images on load
  * libobs: Fix direct rendering test
  * obs-transitions: Use texrender with stacked track mattes
  * obs-transitions: Fix track matte rendering improper sizes
  * obs-transitions: Fix annoying log message
  * obs-transitions: Only check matte duration if matte exists
  * obs-transitions: Free matte texrender when not in use
  * obs-transitions: Remove unnecessary matrix push/pop
  * obs-transitions: Reset track matte texture in tick
  * Revert transition scaling fix
  * frontend-plugins: Fix script properties not updating
  * Revert "rtmp-services: Add Odysee.com"
  * obs-transitions: Blend in linear space
  * rtmp-service: Rename "stream key" for dacast
  * UI: Clear fade to black source
  * UI: Simplify fade to black code
  * cmake: Remove outdated osxbundle files
  * flatpak: Cleanup unwanted static libraries
  * Revert "flatpak: Disable obs-browser build"
  * UI: Disable transition props menu when transitioning
  * rtmp-services: Add Odysee.com
  * rtmp-services: Add Brime Live service
  * obs-filters: Fix unreferenced variable warning
  * libobs: Mark unused parameters
  * libobs: Fix uninitialized variable warning
  * libobs: Fix deadlock removing scene item
  * libobs-winrt,win-capture: Cursor toggle exceptions
  * win-capture: Fix WGC disable index for display
  * image-source: Premultiply alpha in shader
  * libobs: Support 64 bpp images
  * libobs: Add DrawAlphaBlend technique
  * obs-filters: Fix shader for LUT on OpenGL
  * image-source: Allow linear space alpha
  * obs-browser: Add SRGB flag
  * win-capture: Remove SRGB code
  * text-freetype2: Remove SRGB code
  * win-capture: Add OBS_SOURCE_SRGB flag
  * obs-text: Add OBS_SOURCE_SRGB flag
  * mac-capture: Add OBS_SOURCE_SRGB flag
  * linux-capture: Add OBS_SOURCE_SRGB flag
  * image-source: Add OBS_SOURCE_SRGB flag
  * libobs, obs-filters: SRGB backwards compatibility
  * UI: Fix rounding truncation
  * obs-transitions: Remove dead code
  * docs: Remove block quotes (#4621)
  * win-dshow: Add support for ASUS coupled audio
  * obs-browser: Update version to 2.14.2
  * README.rst: Use High DPI Discord Badge
  * UI: Move clearing of copy/paste variables
  * CI: Remove unneeded runtime deps
  * UI: Fix proprty Undo not updating settings properly
  * text-freetype2: Fix empty text not updating source
  * libobs: Add obs_source_reset_settings()
  * UI: Remove duplicate include
  * UI: Fix Undo/Redo for pasting multiple filters
  * obs-filters: Increase opacity precision
  * UI: Add Undo/Redo for single filter copy/paste
  * UI: Add Undo/Redo for pasting multiple filters
  * libobs: Add functions to backup/restore filters
  * obs-filters: Fix bad math in Color Key v1
  * UI: Fix missing files dialog starting hidden (macOS)
  * UI: Fix audio filter changes not being added to undo
  * UI: Fix audio filters being deleted not getting added to undo
  * UI: Fix undo/redo enabling redo with no items in redo
  * obs-filters: Handle premultiplied alpha input
  * libobs: Don't force premultiplied alpha on filters
  * CI: Use a stable version of the Flatpak action
  * UI: Use std::bind for visibility undo/redo action
  * UI: Add Undo/Redo for volume change/mute via main fader
  * UI: Add Undo/Redo items for adv. audio properties
  * UI: Add repeat protection for Undo/Redo
  * UI: Remove unnecessary Undo/Redo cleanup func
  * obs-filters: Use correct branding for NVIDIA Noise Removal
  * UI: Cleanup on_scenes_currentItemChanged function
  * UI: Add undo/redo actions for move up/down/top/bottom
  * text-freetype2: Render in nonlinear space
  * obs-filters: Check NVAFX is enabled before using mutexes
  * libobs: Fix crash in missingfiles when source is invalid
  * obs-filters: Better describe denoiser methods in menu
  * obs-filters: RTX denoiser, initialize only output channels
  * obs-filters: Initialize NVIDIA AFX in a thread
  * image-source: Use DrawNonlinearAlpha
  * libobs: Render async video with DrawNonlinearAlpha
  * libobs: Filter using premultiplied alpha
  * docs: Fix erroneous code example
  * libobs: Add DrawNonlinearAlpha technique
  * UI: Use scene backup/undo/redo funcs for reordering
  * UI: Refactor scene action undo/redo
  * libobs: Add obs_data_get_last_json()
  * obs-transitions: Nonlinear SRGB, swipe
  * obs-transitions: Nonlinear SRGB, slide
  * obs-transitions: Nonlinear SRGB, luma wipe
  * obs-transitions: Nonlinear SRGB, fade
  * obs-transitions: Nonlinear SRGB, fade to color
  * UI: Add missing locale text for reorder undo/redo
  * UI: Add undo/redo for source reordering
  * UI: Fix imported scene collection names duplicating
  * rtmp-services: Update Twitter.com
  * rtmp-services: Add Luzento.com
  * obs-transitions: Crop output of stinger media player
  * obs-transitions: Remove scaling of track matte texture
  * UI: Delete unimplemented declaration, LoadProfile()
  * CI: Use flatpak-builder subaction
  * CI,cmake: Fix macOS version information
  * linux-v4l2: Use flatpak-spawn when inside a Flatpak sandbox
  * UI: Fix crash when closing missing files window
  * UI: Fix invalid check for Remove Multiple Sources dialog result
  * UI: Add Undo/Redo for source visibility
  * UI: Make undo_stack types in-class and private
  * libobs: Add helper func to find a scene by name
  * libobs: Save obs_data json in compact form
  * UI: Fix missing Files dialog crash loading source icon
  * flatpak: Reenable browser source
  * win-dshow: Fix virtual camera CPU usage, add more comments
  * obs-filters: Increase luma key precision
  * mac-virtualcam: Hide logging behind debug flag
  * mac-capture: Add another virtual output loopback device
  * libobs: Return target vec not current when within EPSILON
  * mac-virtualcam: Fix memory leaks
  * UI: Use newer Twitch Dashboard docks for integration
  * obs-filters: Increase brightness precision
  * UI: Increase float property decimals based on step
  * UI: Fix undo data being saved when no changes occur
  * vlc-video: Ignore URLs when checking for missing files
  * CI: Specify arch for prebuilt deps
  * cmake: Automatically copy datatarget PDBs
  * UI: Add Undo/Redo for source visibility transitions
  * libobs: Add transition save/load functions
  * UI: Fix spamming of log when setting current scene
  * azure-pipelines.yml: Remove
  * README.rst: Replace Azure Pipelines badge with GitHub Actions
  * obs-ffmpeg: Expose psycho-aq setting
  * UI: Fix wrong behavior with undo/redo and groups
  * rtmp-services: Update Mixcloud
  * UI: Fix reordering scenes not working properly
  * UI: Update context bar when using undo/redo
  * UI: Force current scene when using undo/redo
  * flatpak: Disable obs-browser build
  * obs-browser: Emit fatal error if CEF or X11 is missing
  * obs-filters: Add color settings to correction v2
  * linux-capture: Ask for PipeWire if deps not found
  * plugins: Set obs-vst as a default requirement
  * plugins: Set obs-browser as a default requirement
  * UI: Fix Undo/Redo holding source references
  * libobs: Add obs_source_is_scene()
  * libobs: Add obs_obj_is_private()
  * libobs: Add obs_source_load2()
  * libobs: Add obs_source_enum_full_tree()
  * UI: Clear undo stack in ClearSceneData() instead
  * UI: Wipe undo/redo stack when switching scene collections
  * UI: Add maximum number of items in undo/redo stack
  * obs-browser: Disable browser panels on Wayland for now
  * win-dshow: Fix libdshowcapture formatting
  * UI: Conform transition duration in Scene Transition dock
  * obs-filters: Code cleanup for RTX denoiser
  * obs-filters: Fix initialization of RTX denoiser
  * linux-capture: De-escalate assertion to a warning
  * win-dshow/libdshowcapture: Update to 0.8.7
  * obs-filters: Perform chroma key in nonlinear space
  * obs-filters: Use new pattern for SRGB support
  * libobs: Add filter functions for SRGB support
  * libobs: Don't save temporarily removed sources
  * libobs: Remove unnecessary null check
  * CI: Enable build cache for the Flatpak workflow
  * flatpak: Use current tree for building OBS
  * Revert "UI: Remove unnecessary IS_WIN32 macro"
  * UI: Remove unnecessary IS_WIN32 macro
  * obs-browser: Update version to 2.14.1
  * UI: Add save notifications to status bar
  * rtmp-services: Update package counter
  * rtmp-services: Include format version in update URL
  * libobs: obs-scene type fixes
  * flibobs: Fix unnecessary truncation
  * libobs/util: Skip pointless free for null
  * libobs/util: Fix warnings for about null usages
  * obs-transitions: Add narrowing casts
  * UI: Ignore scene source which has been removed
  * win-dshow: Fix crashing when using a custom vcam placeholder
  * win-capture: Restore GL capture deduplication
  * UI: Fix crash on exit with stuck encoder
  * UI: Fix character to prevent VS2019 compiler error
  * UI/installer: Add exit codes for silent installer
  * UI: Fix wrong strings for Undo/Redo
  * docs: Document gs_texture_create_from_dmabuf
  * UI: Remove Qt5MacExtras
  * win-capture: Fix window capture stuck last frame
  * UI: Fix UI deadlock after dragging source
  * UI: Fix Horizontal Center Text
  * cmake: Improve OBS_VERSION undefined failure
  * obs-ffmpeg/ffmpeg-mux: Fix hang without global_stream_key
  * UI: Fix locale key name
  * UI: Remove ifdefs for Qt 5.9 and older
  * CI: Quote all bash variables containing paths
  * obs-ffmpeg: Enable macOS hardware decoding for media source
  * libobs: fix property group check
  * obs-x264: Set CRF value conditionally
  * obs-x264: Set sample aspect ratio to 1:1
  * obs-x264: Set timebase
  * CI: Disable PipeWire on Ubuntu
  * flatpak: Expose PipeWire socket
  * linux-capture: Return different descriptions for different captures
  * linux-capture: Add PipeWire-based capture
  * linux-capture: Shuffle around CMake code
  * build: Include gio-unix-2.0
  * libobs, libobs-opengl: add drm format param
  * docs: Update documentation about utility functions for undo/redo
  * UI: Undo/Redo Properties and Filters
  * UI: Undo/Redo context bar properties
  * UI: Undo/Redo Scene Collections
  * UI: Undo/Redo audio
  * UI: Undo/Redo Transformations
  * UI/libobs: Undo/Redo Sources and Scenes
  * UI: Initial Undo/Redo
  * UI: Fix canvas resolution in auto-config
  * flatpak: Don't specify luajit commit
  * obs-browser: Update version to 2.14.1
  * obs-browser: Update version to 2.14.0
  * win-dshow: Check return value of ReadFile
  * win-dshow: Check return values for memory allocation functions
  * win-dshow: Fix incorrect variable used in condition
  * win-dshow: Don't call DisableThreadLibraryCalls in virtualcam
  * win-dshow: Fix memory leak caused by using incorrect API
  * libobs: Fix obs_data_item_numtype returning null in some cases
  * text-freetype2: Updated defaults
  * libobs: Implement obs_data_get_defaults
  * obs-vst: Update to latest version
  * libobs-d3d11: Default to Intel IGPU on IGPU+DGPU systems
  * libobs-d3d11: Split InitFactory to InitAdapter
  * rtmp-services: Add Dacast
  * rtmp-services: Move service-specific files
  * libobs: fix property group check
  * obs-ffmpeg: Missing NVENC bounds check
  * obs-ffmpeg: Replace cast with numeric literal
  * frontend-tools: Remove Qt5X11Extras
  * decklink-output-ui: Remove Qt5X11Extras
  * UI: Add visibility transitions
  * UI: Copy Filters menu is active only if applicable
  * libobs: add helper for source filter count
  * obs-ffmpeg: Static analysis warnings
  * obs-ffmpeg: Use NVENC preset lookahead length
  * obs-ffmpeg: Align NVENC config values
  * obs-ffmpeg: Align NVENC buffer length
  * obs-ffmpeg: Align NVENC lookahead logic
  * obs-ffmpeg: PVT for NVENC fallback
  * obs-ffmpeg: Align NVENC vbvBufferSize
  * obs-ffmpeg: Align NVENC aqStrength
  * obs-ffmpeg: Don't set NVENC max dimensions
  * obs-ffmpeg: Align NVENC dts math
  * obs-ffmpeg: Use av_reduce on NVENC aspect ratio
  * UI: Remove x11info dependency
  * obs-filters: Simplify NVAFX SDK path lookup
  * obs-filters: Minor code cleanup
  * flatpak: Update dependencies
  * UI: Only set AA_DontCreateNativeWidgetSiblings on Wayland
  * obs-filters: Add RTX denoiser
  * rtmp-services: Make YouTube - RTMPS service the default
  * win-capture: Better laptop test for auto-selection
  * libobs: Add function to count GPU adapters
  * UI: Save video settings after 'Resize output (source size)'
  * UI: Add recommended settings for Aparat
  * obs-browser: Update version to 2.13.2
  * UI: Add css on Drag and Drop Adds parsing for the "layer-css" query param of URLs dragged into the main window, similarly to the other layer-* parameters already used.
  * UI: Make drag and drop file ext. case insensitive
  * docs: Add entries for Frontend API T-bar control
  * UI: Add Frontend API function to get value of T-bar
  * libobs: Fix crash when no context
  * UI: Remove UpdateSceneCollection function from header
  * cmake: Fix some Qt files not being logged in CMake output
  * cmake: Require Qt if UI is enabled
  * UI: Set Qt::AA_UseHighDpiPixmaps only on Qt5
  * UI: Explicitly include QFile
  * UI: Don't use QTextStream::setCodec in Qt6
  * UI: Set default string size arg for QT_UTF8 / QString::fromUtf8
  * UI: Force plugins to use version appropriate Qt Network
  * UI: Don't attempt to resize parent group when changing cursor
  * UI: Cleanup Qt for Qt6
  * UI: Fix Qt signal connection warnings
  * frontend-tools: Add edit script button
  * UI: Disable scroll and keyboard input for t-bar
  * UI: Remove unnecessary code
  * UI: Fix grid mode scenes overlapping
  * UI: Fix transform dialog for screen readers
  * UI: Remove redundant code
  * libobs/util: Compiler barriers for ARM64 atomics
  * UI: Fix memory leak with missing files dialog
  * UI: Use clicked signal for buttons in Missing FIles dialog
  * obs-ffmpeg: Fix bug with obs_source_media_play_pause
  * libobs: Minor fixes / code cleanups
  * libobs-d3d11: Avoid temporary ComPtr objects
  * decklink: Remove unnecessary obs-frontend-api dependency
  * UI: Use more accurate wording
  * UI: Fix typo
  * CI: Fix missing entitlements on CEF components for obs-browser
  * mac-virtualcam: DAL PlugIn check for custom png file
  * mac-vth264: Clean up encoder list
  * cmake: Remove pagezero_size from linker options
  * mac-capture: Adjust mHostTime to milliseconds
  * libobs: use clock_gettime_nsec_np() for macOS
  * CI: Update macOS dependencies bundle
  * mac-virtualcam: Handle missing DAL plugin destination directory
  * libobs/util: Split bus name from interface
  * libobs/util: Replace libdbus by GDBus
  * libobs/util: Rename struct field 'id' to 'cookie'
  * rtmp-services: Add ePlay service
  * mac-virtualcam: Fix codesign error after updating OBS
  * CI: Build on Ubuntu 18.04, use newer clang-format
  * UI: Fix output resolution not properly changing
  * UI: Fix locale name
  * obs-ffmpeg: Fix replay save callback not working properly
  * libobs-winrt: Make Close() failures non-fatal
  * graphics-hook: Fix build without COMPILE_D3D12_HOOK
  * win-capture: D3D12 swap chain queue usage
  * flatpak: Enable Wayland
  * libobs-opengl: Implement DMA-BUF importing on EGL renderers
  * deps-glad: Add DMA-BUF EGL extensions
  * libobs/graphics: Add Linux-only gs_texture_create_from_dmabuf()
  * rtmp-services: Add nanoStream Cloud / bintu
  * UI: Fix screen resolution for canvas size
  * flatpak: Disable browser for now
  * Revert "UI: Add ability for stingers to use filters"
  * UI: Check for Expose and PlatformSurface events to create display
  * UI: Make OBSQTDisplay::CreateDisplay() public and allow forcing creation
  * UI: Disable and ignore Always On Top on Wayland platforms
  * UI: Rename callback to match signal name
  * UI: Don't create obs_display when QTToGSWindow fails
  * UI: Destroy display when becoming invisible
  * UI: Retrieve Wayland surface from QWindow
  * libobs-opengl: Introduce an EGL/Wayland renderer
  * libobs-opengl: Try to use the platform display if available
  * libobs: Add a Wayland platform
  * UI: Add ability for stingers to use filters
  * rtmp-services: Add OPENREC.tv service
  * decklink-ui: fix double free of settings
  * win-dshow: Add autorotation toggle
  * rtmp-services: update Piczel.tv recommended
  * obs-transitions: skip stinger size factors if track matte is disabled
  * obs-transitions: default size factors when track matte is disabled
  * obs-transitions: add track matte feature to the stinger transition
  * win-waspi: Make sure to unregister notification obj
  * win-wasapi: Add default audio device change detection
  * libobs/util: More atomic fixes
  * libobs/util: ARM atomic fixes
  * libobs: Include thread names in thread traces
  * Docs: Add obs_frontend_reset_video()
  * Frontend-API: Add obs_frontend_reset_video()
  * libobs: Update compare-exchange pattern
  * docs/sphinx: Update atomic API
  * libobs/util: Various atomic improvements
  * libobs: guard against lagging audio sources
  * libobs: transition: ignore sources with ts=0
  * mac-avcapture: Add additional capture presets
  * UI: Improve missing files text
  * linux-capture: Fail to load when running on EGL
  * UI: Set the Unix platform on startup
  * libobs: Introduce the concept of a Unix platform
  * libobs/nix: Move X11-specific code to obs-nix-x11.c
  * ci: Install qtbase5-private-dev on Linux
  * deps/glad: Make X11 required as well
  * libobs-opengl: Introduce the X11/EGL winsys
  * libobs-opengl: Factor out GLX winsys
  * libobs-opengl: Rename gl-x11.c to gl-x11-glx.c
  * deps-glad: Add EGL
  * UI: Add launch parameter to disable high-DPI scaling
  * obs-outputs: Fix RTMP restart not always working
  * UI: Fix unused parameter
  * UI: Avoid asprintf warning
  * linux-v4l2: Fix ignored return value
  * libobs: Avoid strncpy warning
  * libcaption: Fix static keyword placement
  * rtmp-services: Fix unused parameter
  * obs-filters: Fix unused parameters
  * libobs-opengl: Fix unused parameters
  * libobs: Fix unused parameter
  * libobs: Fix truncation warning on 32-bit Windows
  * linux-v4l2: added range check for try_connect()
  * libobs: Fix leaking obs-internal.h
  * UI: Don't define QT_NO_GLIB
  * UI: Reinstate native dialogs on Linux with browser enabled
  * linux-capture: Ensure locks are initialized
  * rtmp-services: Add PolyStreamer service
  * libcaption: Fix header missing in install
  * CI: Re-enable Python scripting support on CI for macOS
  * obs-scripting: Add Py 3.8+ C-API changes
  * libobs: Duplicate source name for private sources
  * win-capture: Add WGC desktop capture
  * libobs: gs_duplicator_get_monitor_index
  * CI: Enable service integration on Linux
  * libobs-winrt,win-capture: Support desktop capture
  * obs-browser: Fix panel build error on Windows and Linux
  * CI: Use CEF 4280 on GH Actions builds
  * obs-browser: Fix panel build error on macOS
  * obs-browser: Add Linux browser panel support
  * UI: Make BrowserDock native
  * UI: Cleanup native widgets
  * UI: Don't create native widget siblings
  * CI: use a KDE image for Flatpak
  * linux-capture: Fix lock ordering
  * libobs: Add function to get module lib
  * rtmp-services: Update MyFreeCams
  * rtmp-services: Add EventLive
  * rtmp-services: Fix trailing whitespace in services.json
  * UI: Close context menu on destroy of VolControl
  * UI: Fix crash when systray is not enabled
  * linux-v4l2: Improve module detection
  * libobs, linux-v4l2: Set thread names
  * linux-capture: Remove unused code
  * linux-capture: scan for re-created windows more often
  * linux-capture: XSelectInput tracking improvement
  * linux-capture: Capture windows by id first
  * obs-filters: Fix pow arguments
  * libobs: Fix dstr leak
  * obs-browser: Update color handling
  * obs-filters: Apply sharpness filter in linear space
  * obs-filters: Apply scale filter in linear space
  * obs-filters: Apply image mask filter in linear space
  * obs-filters: Apply GPU delay filter in linear space
  * obs-filters: Apply luma key filter in linear space
  * obs-filters: Apply color key filter in linear space
  * obs-filters: Apply color grade filter in linear space
  * obs-filters: Apply color correction filter in linear space
  * obs-filters: Apply chroma key filter in linear space
  * obs-transitions: Linear SRGB, swipe
  * obs-transitions: Linear SRGB, slide
  * obs-transitions: Linear SRGB, luma wipe
  * obs-transitions: Linear SRGB, fade
  * obs-transitions: Linear SRGB, fade to color
  * linux-capture: Support linear SRGB
  * mac-capture: Support linear SRGB
  * win-capture: Support linear SRGB
  * text-freetype2: Support linear SRGB
  * obs-text: Support linear SRGB
  * libobs-winrt: Support linear SRGB
  * image-source: Support linear SRGB
  * UI: Render previews in linear sRGB space
  * libobs: Final downsample with SRGB formats
  * libobs: Deinterlace as linear SRGB when needed
  * libobs: Update render_item to enable linear SRGB
  * docs/sphinx: Document SRGB changes
  * libobs: Add dormant SRGB format support
  * linux-v4l2: Add auto reset on timeout option
  * Revert "mac-avcapture: Add additional capture presets"
  * mac-avcapture: Add additional capture presets
  * UI: fix the maximum search length of Hotkeys Filter
  * libobs-opengl: SRGB-safe GLSL path for raw loads
  * UI: Replace deprecated QLayout->setMargin with setContentsMargin
  * libobs: Add os_is_obs_plugin function
  * ci: Add experimental Flatpak bundle
  * build-aux: Add Flatpak manifest
  * .gitignore: Remove duplicated .DS_Store
  * CI: Enable service integration in GitHub Actions
  * UI: fix unable to upload and view crash report in mac
  * deps: Update cmake_minimum_required to 2.8.12
  * obs-outputs: Use system-wide FTL if present
  * UI: Add interact button to source toolbar
  * UI: Fix color of filters icon
  * mac-virtualcam: Make DAL plugin filename case consistent
  * CI: Fix CEF version for both Linux & macOS
  * obs-browser: Update to 2.11.0
  * UI: Add missing files dialog
  * libobs: Add missing file API to sources
  * UI: Add support for OBS_PLUGINS*_PATH env variables
  * UI: Add virtual camera to system tray
  * libobs-winrt: Disable WGC border on insider SDK
  * libobs-winrt: Fix potential race crash
  * UI: Use FileNameWithoutSpace for screenshot output
  * rtmp-services: Use official Twitch endpoint to fetch ingests
  * rtmp-services: update Piczel.tv recommended
  * obs-frontend-api: Add frontend api functions for the virtual camera
  * UI: Support FTL URLs for custom streaming service
  * UI: Only apply passthrough DPI scaling on Windows
  * obs-ffmpeg: Always fully restart remote media sources
  * ftl-stream: Fix reconnect loop on FTL ingest disconnect
  * rtmp-services: Add Glimesh service
  * libobs: Cleanup uses of objc_msgSend in Objective-C code
  * UI: Fix crash when no audio backends are available
  * linux-v4l2: Improve error and debug logging
  * AUTHORS: Update authors from git
  * .mailmap: Disambiguate many more authors
  * cmake: Make mac vcam optional (enabled by default)
  * UI: Refactor importer to use GetUnusedSceneCollectionFile
  * UI: Make GetUnusedSceneCollectionFile usable elsewhere
  * win-capture: Typeless game capture textures
  * libobs-d3d11: Support typeless textures
  * libobs: Fix missing Linux libraries with certain flags
  * obs-filters: Fix color overlay in color correction
  * docs/sphinx: Add obs_properties_add_color_alpha
  * libobs: Support color picker with alpha
  * UI: Support color picker with alpha
  * obs-qsv11: Fix bframe=0 not working
  * .gitattributes: Normalize en-US.ini
  * libobs: Fix gs_duplicator_get_texture function check
  * CI: Fix cef version in full build
  * CI: Add dynamic number of processors to make calls on CI
  * CI: Force use of system-provided binaries for build script
  * libobs: Update version to 26.1.2
  * CI: Update Windows dependencies to VS2019 versions
  * CI: Update Windows Qt from 5.10.1 to 5.15.2
  * CI: Update macOS to CEF 4183
  * obs-browser: Update to 2.10.9
  * rtmp-services: Add CamSoda service
  * rtmp-services: Add MyFreeCams
  * UI: Enable HW acceleration switch for browser sources on Mac
  * libobs: Add texture sharing support for macOS/OpenGL
* Thu Apr  8 2021 Jimmy Berry <jimmy@boombatower.com>
- Remove ffmpeg restriction to version 3 to avoid segfault.
* Wed Jan  6 2021 jimmy@boombatower.com
- Update to version 26.1.1:
  * win-dshow: Fix dshowcapture not linking audio of certain devices
  * linux-jack: fix deadlock when closing the client
  * linux-jack: mark ports as JackPortIsTerminal
  * linux-jack: fix timestamp calculation
  * obs-browser: Initialize CEF early to fix macOS crash
  * libobs: Update version to 26.1.1
  * rtmp-services: Add Loola.tv service
  * rtmp-services: Fix json formatting
  * libobs: Avoid unnecessary mallocs in audio processing
  * UI: Fix padding on Acri context bar buttons
  * image-source: Fix slideshow transition bug when randomized
  * docs/sphinx: Add missing obs_frontend_open_projector
  * libobs: Update to SIMDe 0.7.1
  * libobs: Set lock state when duplicating scene item
  * libobs: Add definitions in ARCH_SIMD_DEFINES
  * cmake: Add ARCH_SIMD_DEFINES variable
  * coreaudio-encoder: Fix cmake for mingw
  * Revert "UI: Only apply new scaling behavior on newer installs"
  * UI: Only apply new scaling behavior on newer installs
  * UI: Support fractional scaling for Canvas/Base size
  * mac-virtualcam: Remove unnecessary logging
  * mac-virtualcam: Mark parameters as unused
  * image-source: Add .webp to "All formats" option
  * image-source: Add webp to file filter
  * CI: Remove jack, speex and fdk-aac from default builds for macOS
  * libobs, obs-ffmpeg: Use correct value for EINVAL error check
  * UI/updater: Increase number of download workers
  * UI/updater: Enable HTTP2 and TLS 1.3
  * UI: Fix name of kab-KAB locale
  * decklink: Fix automatic pixel format detection
  * CI: Fix macOS 10.13 crashes due to unsupported library symbols
  * UI/installer: Add additional VS2019 DLL check
  * mac-virtualcam: Fix file mode
  * CI: Run make with -j$(nproc)
  * CI: Remove obsolete and unused files
  * libobs: Add texture sharing support for macOS/OpenGL
  * CI: Add necessary changes for CEF 4183
  * UI/updater: Move in-use files away before writing
  * UI/updater: Always clean up temporary files
  * UI: Remove Smashcast from AutoConfig
  * rtmp-services: Remove Smashcast
* Tue Dec 15 2020 Jimmy Berry <jimmy@boombatower.com>
- Add modinfo-use-full-path.patch for new v4l2lookback support.
* Tue Dec 15 2020 jimmy@boombatower.com
- Update to version 26.1.0:
  * UI: Add deferred function to update context bar
  * UI: Fix installer/updater check for vs2019 32bit
  * Update translations from Crowdin
  * Revert #3856
  * linux-jack: fix timestamp calculation
  * linux-jack: fix deadlock when closing the client
  * linux-jack: mark ports as JackPortIsTerminal
  * linux-pulseaudio: fix race conditions
  * obs-browser: Add obsExit event
  * UI: Determine rate control after creating encoders
  * UI: Handle (de)select scene items queued
  * CI: Update macOS to Qt 5.15.2 and deps 2020-12-11
  * libobs: fix the pending stop trick
  * UI/updater: Fix dll check
  * UI: Remove jansson requirement from UI and updater
  * UI/updater: Update redist checks to VS2019
  * deps/json11: Update to most recent version
  * rtmp-services: Update Steam
  * libobs: Update version to 26.1.0
  * sndio: remove strerror_l
  * UI: Fix weird spacing in adv output FFmpeg recording
  * linux-v4l2: Fix bashism in v4l2loopback module detection
  * obs-scripting: Fix removing signal handlers in lua
  * UI: Correctly unregister Virtual Camera & Source Toolbar hotkeys
  * UI: Scale Interact cursor position based on display DPI
  * UI: Sync 'Copy Filters' enabled state in the Source context menu
  * mac-virtualcam: Build a universal x86_64+arm64 binary for M1 Macs
  * vlc-video: Free media struct
  * mac-virtualcam: Fix remaining global namespaces
  * UI: Allow enabling vod track on custom via ini
  * UI: Fix vod track working with custom server
  * UI: Fix vod track not working with twitch soundtrack
  * UI: Fix aac encoder name
  * libobs: Ignore non-fatal ffmpeg return values during remux
  * UI: Fix disabled sliders
  * UI: Remove redundant setting
  * UI: fix typo
  * UI/installer: Add additional VS2019 DLL check
  * UI: Use Qt::MiddleButton instead of deprecated Qt::MidButton
  * obs-browser: Update to 2.9.0
  * UI: Don't round non-integer High DPI scale
  * CI: Add decklink-captions to dylibbundler fixups
  * enc-amf: Fix inability to set bitrate in latest AMD driver
  * UI: Fix filter window rendering and accessible names
  * UI: Log success/failure for scene collection importer
  * UI: Prevent import failure for collections with slash in name
  * UI: Prevent name collision during scene collection import
  * UI: Various screen reader fixes
  * Update translations from Crowdin
  * libobs: Allow wrapping D3D11 object with gs_texture_t
  * UI: Fix Save Replay button staying highlighted
  * frontend-tools: Don't give every loaded filter focus
  * UI: Set default source toolbar visibility to true
  * obs-outputs: Log unhandled status description as debug level
  * mac-virtualcam: Fix global namespace issues in DAL plugin
  * cmake: Make sure to copy other mbedtls libraries
  * obs-browser: Don't inject CSS if the property is empty
  * UI: Force plugins to use our Qt5Network, not their own
  * cmake: Add Qt5Network to copied windows libs
  * CI: Remove explicit LANGUAGE flags for cmake 3.19+
  * obs-ffmpeg: Treat non-network errors as fatal too
  * Revert "obs-ffmpeg: Treat errors as fatal for non-network streams in ffmpeg-mux"
  * mac-virtualcam: Remove old test card
  * UI: fix build on older FreeBSD versions
  * win-capture: Update hook version
  * obs-ffmpeg: Treat errors as fatal for non-network streams in ffmpeg-mux
  * obs-ffmpeg: Treat EINVAL as non-fatal in ffmpeg-mux
  * win-capture: Clean up remaining /W4 warnings
  * obs-ffmpeg: Treat AVERROR_INVALIDDATA as non-fatal
  * obs-ffmpeg: Add error detection to ffmpeg-mux network streams
  * deps/media-playback: Fix audio segment duration calc
  * autotools: Remove config module
  * Revert "obs-ffmpeg: Add error detection to ffmpeg-mux"
  * mac-virtualcam: Update locales
  * UI: Detect other instances of obs on FreeBSD
  * win-capture: Fix our own Vulkan spec violation
  * Add sndio support (#3715)
  * Add OpenBSD support
  * UI: Add Twitch VOD track to simple output mode
  * cmake: Put decklink-captions in source folders
  * win-dshow: Add support for YUY2 in virtualcam
  * UI: Move "changed" when recreating output res widget
  * UI: Show service max resolution/framerate values to user
  * UI: Add service res/fps limitation support to settings
  * libobs: Change service max res. to res. list
  * UI: Allow blocking all signals if resetting downscales
  * UI: Add SetComboItemEnabled
  * win-capture: Warning fixes
  * libobs-winrt: Fix misnamed function
  * UI: Use macOS app icon for Qt app on macOS
  * UI: Fix tray icon menu handling on macOS
  * UI: Update macOS app icon
  * UI: Update tray icons to use masks on macOS
  * win-capture: Fix unused variables
  * UI: Fix compiler-specific error
  * UI: Move "enforce" setting to "ignore" stream section
  * UI: Refactor to make it easier to get service object
  * libobs: Implement obs_service func to get max bitrates
  * rtmp-services: Increase twitch audio bitrate
  * decklink: Fix compiling on linux
  * rnnoise: Explicit double to float conversions
  * rtmp-services: Add missing int cast
  * obs-ffmpeg: Add missing int cast
  * libobs-winrt: Fix BOOL/bool mismatch warning
  * libobs: Fix bad type and size mismatch
  * UI: Add VOD track support in advanced output
  * decklink: Clean up warnings introduced by caption code
  * CI: Remove caching of obs-deps for Github CI
  * decklink: Upgrade sdk to version 11.6
  * Remove BUILD_CAPTIONS build flag
  * decklink: Fix format detection loop
  * decklink: Add ability to ingest/embed cea 708 captions
  * linux-v4l2: avoid OOB write
  * linux-v4l2: Hide modinfo from terminal
  * UI: Don't update source context bar when hidden
  * vlc-video: Use case insensitive compare for valid extension check
  * CONTRIBUTING.rst: Update CONTRIBUTING doc
  * UI: Disable stream encoder setting in simple output with active output
  * Add virtualcam plugin to OBS codebase
  * UI: Detect other instances of obs on Linux
  * UI/installer: Use random temp directory for security
  * libobs: Add desktop session type to Linux log
  * rtmp-services: Add YouTube RTMPS beta service
  * rmtp-services: Add Viloud service
  * linux-v4l2: Add virtual camera output
  * win-dshow: Fix virtualcam crash and reference bug
  * UI: Add max cx/cy/fps clamp (if service specifies)
  * rtmp-services: Add max recommended cx/cy/fps for Facebook
  * rtmp-services: Add specifiable max cx/cy/fps in json
  * libobs: Add ability to get max cx/cy/fps from service
  * obs-ffmpeg: Add MX350 to blacklist
  * UI: Run Autoconfig Wizard on New Profile Creation
  * CI: Update macOS build script to support alternative build configs
  * obs-transitions: Expose hardware decoding for Stingers
  * libobs: Return default obj and array rather than current
  * UI: Report detailed output errors for Replay Buffer
  * CI: Fix Windows artifact issues and housekeeping
  * UI: Fix replay buffer saved event in advanced mode
  * docs: Fix GitHub Actions doc check warnings
  * linux-alsa: Support more device formats
  * UI: Detect other instances of obs on macOS
  * UI: Add duplicate filter
  * obs-filter: Fix potential symbol clashing on Linux
  * UI: Update Twitch Get Stream Key link
  * UI: Apply minimum width to Stats fields
  * UI, libobs: Add ability to copy/paste single filter
  * UI: Keep showing time when paused
  * obs-ffmpeg/ffmpeg-mux: Fix issue with HLS
  * obs-ffmpeg: Add ability to debug ffmpeg-mux subprocess
  * UI: Fix text clipping on non-English locales in certain locations
  * win-capture: Fix D3D leaks on swap chain release
  * rtmp-services: Add YouTube HLS service selection
  * obs-ffmpeg: Add HLS output
  * obs-ffmpeg: Allow using stream keys with muxer
  * obs-ffmpeg: Allow specifying mux settings directly
  * obs-ffmpeg/ffmpeg-mux: Use separate printable URL target
  * obs-ffmpeg/ffmpeg-mux: Set codec->time_base if avformat < 59
  * obs-ffmpeg/ffmpeg-mux: Add ability to get FFmpeg logging
  * UI: Find YouTube via starting string, not full match
  * UI: Add support for "More Info" link from service
  * obs-ffmpeg/ffmpeg-mux: Fix variable case
  * obs-ffmpeg: Move muxer structure/funcs to header
  * UI: Fix replay buffer frontend event not triggering
  * UI/obs-frontend-api: Fix replay buffer save event ABI break
  * UI: Add replay buffer saved event to the frontend api (#3592)
  * UI: Prevent disabling replay buffer if it's active
  * CI: Add virtualcam GUID to win builds
  * CI: Remove deprecated use of `set-env` in Github Actions
  * Docs: Fix Frontend Finish Loading event
  * UI: Set focus back to label after source rename
  * UI: Apply custom_rtmp service settings to srt output
  * rtmp-services/rtmp-custom: Apply repeat_headers video setting to srt output
  * obs-ffmpeg: Allow video headers repetition in IDR and bitstream for jim-nvenc
  * obs-x264: Allow repeat_headers and annexb parameters to be set
* Mon Oct 19 2020 Jimmy Berry <jimmy@boombatower.com>
- Remove c7f84f8fc4e90ef779a204ac268f5ee1a962e324.patch.
- Add fix-luajit-include-path.patch from palica@liguros.net to
  resolve Lua script building.
* Wed Oct  7 2020 jimmy@boombatower.com
- Update to version 26.0.2:
  * UI: Fix selecting correct transition when deleting
  * UI: Fix non-default transitions going below add vals
  * libobs: Update version to 26.0.2
  * UI/installer: Add avutil/swscale to file in use check
  * coreaudio-encoder: Actually fix coreaudio loading
  * libobs: Update version to 26.0.1
* Mon Oct  5 2020 jimmy@boombatower.com
- Update to version 26.0.1:
  * coreaudio-encoder: Fix path on windows
  * coreaudio-encoder: Refactor windows import
  * rtmp-services: Update AfreecaTV
  * Revert "UI: Delete existing fullscreen projector"
  * win-capture: Update hook version
  * win-dshow: Fix decoupled audio with EVGA/magewell
  * libobs-winrt: Use native cursor draw for WGC
  * win-capture: Violate Vulkan spec for compatibility
  * obs-ffmpeg: Add error detection to ffmpeg-mux
  * obs-ffmpeg: Signal a remote disconnect for network streams from ffmpeg-mux
  * Revert "mac-capture: show actual windows in Window Capture sources"
  * UI: Greatly improve main window repaint performance
  * win-capture: Fix mask handling on some color cursors
  * CI: Fix swig dependency on FreeBSD
  * cmake: Fix finding libfdk header path
  * UI: Fix tab order for controls dock
  * CI: Use tag number only for macOS plist when triggered by version tag
  * rtmp-services: Remove weabook.live
  * UI: Skip ChromeOS test on FreeBSD
  * rtmp-services: Set actual integer value of bframes in services
  * UI: Implement exit on CTRL + Q for linux
  * UI: Disable QT's implicit colourspace conversion on macOS
  * UI: Move "Add [transition]" to bottom of combo
  * UI/updater: Fix cmd prompts popping up registering vcam
  * UI/updater: Fix race condition
* Mon Sep 28 2020 jimmy@boombatower.com
- Update to version 26.0.0:
  * libobs: Update version to 26.0.0
  * Fix translator names
  * Update translations from Crowdin
  * UI: Clarify system tray code
  * UI: Fix formatting
  * UI: Miscellaneous code cleanups
  * UI: Fix "Add [transition]" not being translated
  * UI: Add translation for "Add [x]"
  * UI: Always parse log contents for Log Viewer as UTF-8
  * v4l2-linux: Fix fourcc order
  * v4l2-linux: Fix nv12 linesize
  * UI: Fix screenshots preventing auto-remux
  * UI: Use correct APPDATA for installer
  * UI: Various installer script updates
  * rtmp-services: Updatge Vaughn Live / iNSTAGIB & Breakers
  * deps/media-playback: Fix time at non-standard speeds
  * libobs: Check if output active when setting encoders
  * frontend-tools: Free xdisplay on Linux auto scene switcher
  * UI: Add file-in-use check for virtualcam module dlls
  * rtmp-services: Added Mux to services.json
  * UI: Create output before calling start stream event
  * UI: Do not always have log viewer loaded
  * win-dshow: Set current working directory in VirtualCam scripts
  * linux-v4l2: Fix boolean and menu control types
  * UI: Fix certain buttons turning up white in dark theme
  * obs-scripting: Fix script_path() python mem corruption
  * UI:Fix crash on log upload
  * CI: Update notarisation process for Github CI
  * obs-ffmpeg: Add missing translable string for "Profile"
  * CI: Sign and notarize macOS builds on new tags
  * win-capture: Increment graphics hook version
  * CI: Fix Azure macOS pipeline to use new build script
  * obs-filters: Remove unnecessary files
  * obs-filters: Use builtin rnnoise dep if not found
  * CI: Bump macOS-deps version to include rnnoise
  * obs-ffmpeg: fix crash with rawvideo
  * UI: Fix recording check when using url output
  * CMake: Set PIC for all library targets
  * UI: Unset bandwidth test on non-Twitch service / disconnect
  * UI: Don't warn about bandwidth test mode if not authed
  * rtmp-services: Add SHOWROOM
  * win-capture: Improve game capture messages
  * deps/media-playback: Fix fast-forward after reset
  * win-dshow: Fix bug determining closest audio config
  * UI: Fix vcam button not changing colors when checked
  * UI: Replace/simplify device toolbar
  * win-dshow: Add "activate" proc to proc handler
  * win-dshow: Fix 24bit audio not being detected correctly
  * win-dshow: Fix AJA devices crashing
  * UI: Remove duplicate media timer code
  * libobs: Deprecate service multitrack check
  * deps/media-playback: Fix pause continually running loop
  * UI: Remove redundant word
  * enc-amf: Update AMD encoder submodule
  * UI: Fix scene tree event handling
  * Update VIDEO_CS_DEFAULT to mean 709 instead of 601
  * win-dshow: Add VirtualCam installer scripts
  * cmake: Add function for installing data from abs path
  * win-dshow: Use cmake-based GUID for virtualcam
  * UI: Ensure tray icon is themed in all cases
  * UI: Change the default color setting in the UI from sRGB to 709
  * UI: Refine context bar
  * UI: Allow adjusting media slider with arrow buttons
  * UI: Use correct constant for CryptDecodeObjectEx
  * libobs/media-io: Fix suspicious memset behavior
  * UI: Set restart state when there is no media
  * UI: Make SetupOutputs virtual instead of ignoring vcam
  * UI: Save Freetype Text source color from Source Toolbar
  * win-capture: Put window capture update data in a mutex
  * UI: Fix auto-remux not working w/ slash filesnames
  * UI: Do not show tray icon if not active
  * UI: Do not show media controls on network media source
  * UI: Fix crash when starting vcam before other outputs
  * UI: Fix maximum size on image source toolbar
  * UI: Fix source toolbar color selection on color source
  * UI: Fix studio mode load bug
  * UI: Fix rec time left not showing in stats
  * vlc-video: Fix format conversion typos
  * UI: Fix memory leak when dropping files
  * UI: Fix source ref bug causing crash on exit
  * mac-capture: Filter non-trivial windows
  * win-capture: Fix Vulkan crash on minimize restore
  * win-capture: Add Vulkan instance creation fallback
  * win-capture: Vulkan variable naming consistency
  * UI: Fix compiler warning about needing parenthesis
  * docs/sphinx: Fix mismatched typedefs
  * docs/sphinx: Fix incorrect callback information
  * CI: Remove clang format Mac check
  * win-dshow: Add file description for virtual camera DLL
  * obs-vst: Support older Qt versions
  * win-dshow: Use constant reference for virtualcam CLSID
  * win-dshow: Reduce size of virtualcam placeholder image
  * libobs: Check data validity for media sources
  * vlc-video: Fix possible undefined behavior in format conversion
  * obs-vst: Fix VST detection in home directory on Linux
  * obs-browser: Update to 2.8.7
  * CI: Update macOS deps to fix crash from invalid linking
  * obs-filters: Cleanup CMake
  * UI: Add missing tab stop fields in Settings
  * UI: Fix compile warnings about deprecated QT usage
  * libobs: Log Windows 10 Hardware GPU Scheduler
  * plugins: Clear compile warnings on Linux
  * UI: Fix output channels not being deleted
  * UI: Disable scene rename shortcut key while renaming
  * UI: Fix tray icon appearing when disabled in settings
  * win-capture: Fix excessive window capture logging
  * UI: Remove unnecessary obs_properties_apply_settings
  * UI: Defer device properties to separate thread
  * UI: Put context combo box operations in functions
  * CI: Update macOS CLI build script
  * UI: Make image source toolbar expand
  * UI: Disable properties button if no properties
  * UI: Remove null source warnings
  * UI: Clear context bar on scene collection change
  * UI: Align Advanced Audio Percent toggle to Volume text
  * UI: Add maximize and minimize support to Log Viewer
  * UI: Bring Log Viewer to front instead of closing
  * CI: Add Sphinx Docs generator Github Action
  * obs-outputs: Remove legacy multitrack code
  * UI: Don't open second dialog if close event is ignored
  * obs-ffmpeg: Fix crash when seeking with no media
  * UI: Fix projector not working on secondary monitors
  * obs-filters/obs-outputs: Cleanup unused var warns
  * win-capture: Robust Vulkan swap chain handling
  * UI: Fix always on top w/ projectors on Linux
  * UI: Add OBSBasic::ClearProjectors()
  * UI: Fix transition enumeration
  * UI: Change cursor when interacting with the preview
  * UI: Fix hotkeys auto repeating
  * obs-filters: Fix building without noise reduction
  * win-capture: Update graphics hook version
  * obs-outputs: Check support for mbedtls func
  * obs-outputs: Fix Windows memory leak
  * UI: Fix multiview update regression
  * obs-outputs: Add support for metadata-based multitrack
  * obs-outputs: Don't assume @setDataFrame
  * obs-x264: Fix memory leak
  * libobs: Fix underlinking X11
  * text-freetype2: Fix x,y bounds for text outline and shadow
  * libobs-winrt: Device loss crash prevention
  * win-capture: Remove unused strings
  * UI: Do not process unnamed sources for hotkeys
  * UI: Render tabs and spaces in Log Viewer
  * obs-outputs: Enable Windows mbedTLS threading support
  * UI: Change default sample rate to 48 kHz
  * obs-filters: Add option to use RNNoise for noise reduction
  * UI: Fix obsolete filters showing up
  * oss-audio: Improve /dev/sndstat parsing on FreeBSD
  * obs-x264: Discard excess warning for e2k
  * cmake: Discard excess warnings for e2k
  * cmake: Enable SIMD for Elbrus architecture
  * cmake: Conditionalize -fopenmp-simd
  * UI: Source Toolbar
  * image-source: Transition when restarting slideshow
  * obs-scripting: Fix removing signal handlers in python Closes #3218
  * UI: Provide Open button in the Log Viewer
  * UI:Show "Get Stream Key" to users of Facebook CDN
  * image-source: Use media control api for slideshow
  * Revert "image-source: Add proc handler calls to slideshow"
  * CI: Add QtNetwork to bundle to restore Streamdeck support
  * README.rst: Remove Mantis
  * libobs: Add functions to get locale text from modules
  * libobs: Add function to get module pointer
  * libobs: Add OBSRef::Get()
  * image-source: Add proc handler calls to slideshow
  * image-source: Play if play_pause() called while stopped
  * UI: Add missing refresh icon to acri qss file
  * libobs: Fix undefined behavior
  * win-capture: Remove Vulkan CTS workaround
  * mac-decklink: Fix C++ virtual function warnings
  * CI: Update macOS deps version to fix unmet Qt plugin dependencies
  * libobs: Fix deferred update sometimes using stale data
  * UI: Clarify and improve locale text
  * UI: Move View -> Toolbars -> Listboxes
  * UI: Remove unused action
  * UI: Mac fix — remove wizard background padding
  * UI: Check and fail when launched under ChromeOS
  * UI: Remove unused variable
  * UI: Add log viewer window
  * frontend-tools: Add "Open file location" menu item for scripts
  * frontend-tools: Add context menu to Scripts list
  * UI: Redesign transitions dock
  * UI: Use case-insensitive sort for "show all" services
  * UI: Add ability to make screenshots
  * UI: Simplify path generation code
  * oss-audio: Use util_mul_div64() to do time scaling
  * obs-ffmpeg: Set async video frame immediately when seeking
  * deps/media-playback: Add seek callback
  * libobs: Add func to set async video frame immediately
  * CI: Fix Brew Bundler breaking without prior brew update
  * rtmp-services: Add api.video service
  * rtmp-services: Add Nimo TV auto server
  * UI: Make macOS 'always on top' more aggressive
  * UI: Fix clickable text on properties with tooltips
  * libobs: Add util/sse2neon.h to CMakeLists
  * obs-qsv11: Fix bug mapping old qsv settings to new
  * libobs: Call enum_all_sources in check for enum_all_sources
  * win-capture: Make Vulkan frame data local to queue
  * win-capture: Hide Vulkan linked list internals
  * win-capture: Improve Vulkan hook stability
  * obs-ffmpeg: Clear texture when starting playback
  * libobs: Update async texture when showing preloaded video
  * UI: Remove OBSContext class and shutdown in run_program
  * CI: Disable Python on macOS
  * CI: Disable Python for Mac PR automation
  * CI: Remove Mixer cmake variables
  * rtmp-services: Remove Mixer servers and checks
  * UI: Remove Mixer integration
  * deps/media-playback: Don't EOF while paused and seeking
  * deps/media-playback: Preload video when seeking paused
  * win-dshow: Fix virtual camera filter name
  * win-dshow: Fix virtual camera enable bug
  * rtmp-services: Fix memory leak
  * obs-ffmpeg: Fix race and deprecation warnings
  * libobs/media-io: Add missing codec_tag set
  * deps/media-playback: Remove unused #define
  * deps/libff: Remove very old version check
  * UI: Fix warning about missing override
  * UI: Switch 601 to sRGB as default color space
  * UI: Add sRGB option to colorSpace output setting
  * media-playback: Leverage VIDEO_CS_SRGB
  * obs-x264: Improve color space handling
  * obs-ffmpeg: Improve color space handling
  * libobs: Add VIDEO_CS_SRGB support
  * obs-ffmpeg: Fix FFmpeg deprecation warnings
  * libobs/media-io: Fix FFmpeg deprecation warnings
  * libobs: Fix FFmpeg deprecation warnings
  * UI: Add flag/file to disable built-in updater
  * frontend-tools: Make links in script description clickable
  * UI: Use non-native file dialog w/ Linux
  * rtmp-services: drop Restream.io FTL support
  * libobs: Add arm support
  * UI, obs-ffmpeg, obs-filters: Fix compile warnings
  * coreaudio-encoder: Fix encoding of 4.0 speaker layout
  * deps/media-playback: Reset TS when seeking
  * CI: Disable building OBS with Python scripting support on macOS
  * CI: Add fix for macOS builds failing on push for Azure CI
  * rtmp-services: Update Uscreen service
  * win-capture: Log duplicator display when updating properties
  * linux-v4l2: Fix case of variables to snake_case
  * obs-outputs: Use FLV codec IDs for videocodecid/audiocodecid
  * obs-ffmpeg: Fix play pause crash
  * libobs/util: Use is_padding() for wcsdepad as well
  * libobs/util: Fix potential crash
  * Revert "UI: Match Windows taskbar state to tray icon"
  * Revert "Merge pull request #3110 from WizardCM/taskbar-color-setting"
  * libobs: Translate F13-F24 hotkeys on Windows
  * win-capture: Remove fixed-size Vulkan arrays
  * rtmp-services: Add "Taryana - Apachat" streaming service
  * UI: Add setting for taskbar color
  * UI: Add informative messages to auto-config dialog
  * UI: Set remove prompt default action
  * win-capture: Fix 32-bit Vulkan capture
  * CI: Update build script to use pre-built SWIG and QT dependencies
  * obs-qsv11: Simplify UI quality parameters
  * obs-qsv11: Enable VDEnc on ICL+
  * obs-qsv11: Add latency mode to QSV settings
  * UI: Update Facebook get stream key URL
  * UI: Make color consistent, don't show alpha value
  * obs-qsv11: Set preference for encode to iGPU in case of i+i
  * UI: Delete projector when monitor is disconnected
  * obs-ffmpeg: Allow continuous network streaming
  * UI: Show help text for launch parameters on Windows
  * libobs: Fix video scalar copy heights
  * UI: Add virtual camera to UI
  * win-dshow: Add Virtual Camera (Windows)
  * UI: Add TBar controls to obs-frontend-api
  * UI: Allow the use of Esc key to quit settings window
  * frontend-tools: Add defaults button to script dialog
  * obs-ffmpeg: Add auto reconnect to remote media sources
  * UI: Fix scene switcher not detecting some windows
  * UI: Fix unreadable Connecting Stream button
  * win-capture: Don't use Chrome classes for priority
  * win-capture: Decouple swap and frame indices
  * obs-ffmpeg, UI: Allow slash in recording names
  * UI: Add always on top checkbox to projector context menu
  * mac-capture: Add several virtual audio drivers to Desktop audio
  * libobs: Add sample unit tests leveraging cmocka
  * CI: Quick fix to cover pre-installed Homebrew dependencies for macOS
  * UI: Add window projector option "fit to content"
  * rtmp-services: Add weabook.live
  * UI: Fix pause/replay buttons having large width
  * rtmp-services: Update Lahzenegar RTMP
  * win-capture: Remove game capture scaling
  * UI: Update volmeters at 60hz
  * UI: Fix warnings for Qt 5.15
  * rtmp-services: Remove offline servers/services
  * win-capture: Reset command pool rather than buffer
  * rtmp-services: Add VIMM
  * color-source: Change default color to d1d1d1
  * rtmp-services: Update AfreecaTV
  * UI: Enable Get Stream Key Button for Trovo service
  * rtmp-services: Update Madcat service
  * UI: Add 64bit windows checks to installer
  * libobs: Reset audio data on timestamp jump
  * rtmp-services: add angelthump
  * UI/updater: Use 1 MB static memory for hashing
  * UI/updater: Fix running updater as different user
  * UI/updater: Exit with error if elevation failed
  * obs-outputs: Log unhandled rtmp status responses
  * obs-outputs: Handle rtmp NetStream.Publish.BadName response
  * UI: Don't try to create service if missing file
  * UI: Don't try to load replay buffer hotkey if null
  * libobs: Fix right edge for "video scaler"
  * libobs: Fix right edge of some videos
  * libobs: Fix right edge for JPEG images
  * UI: Auto update projector settings
  * UI: Fix projector always on top not working on Linux
  * UI: Delete existing fullscreen projector
  * deps/media-playback: Use SWS_POINT instead of SWS_FAST_BILINEAR
  * deps/media-playback: Use OBS YUV(A)444P to RGB conversion
  * libobs: Use autoreleasepool for graphics thread
  * win-capture: Remove dead VkResult values
  * libobs/media-io: Remove unused code
  * oss-audio: Add en-US translation data file
  * UI: Fix GetPreferredLocales locale detection
  * cmake: Update minimum Windows SDK version
  * UI: Update NSIS installer script
  * libobs-winrt: Require Windows 10 SDK 19041
  * image-source: Don't check for changes when hidden
  * Revert "Merge pull request #2993 from brittneysclark/enable_vdenc"
  * rtmp-services: Add Mixcloud
  * libobs: Unload modules while OBS core is active
  * libobs: Remove excessive null checks
  * libobs: Use correct data pointer for hotkey pair
  * win-capture: Improve Vulkan synchronization
  * libobs: Fix os_get_executable_path_ptr on Linux
  * libobs-winrt: Move project to core VS filter
  * cmake: SIMDe & GCC? then enable OpenMP 4 SIMD
  * libos: Freshen SIMDe code copy
  * docs: Remove Doxyfile
  * docs: Remove Doxygen
  * obs-qsv11: Simplify UI subjective quality parameters
  * UI: Change audio device string in settings
  * CI: Improve formatcode.sh efficiency
  * obs-filters: Misc code cleanups detected by PVS Studio
  * linux-v4l2: Selective stream restart
  * obs-ffmpeg: Show friendly error for NV_ENC_ERR_INVALID_VERSION
  * UI: Set 8x8 as minimum selectable resolution
  * UI: Add percent checkbox to advanced audio dialog
  * win-capture: Better matching of internal UWP windows
  * UI: Don't show alpha value for color source
  * UI: Fixed case to match what the files are named
  * CI: Require VLC in CI builds, Fix VLC
  * cmake: Fix warnings and normalize variables/errors
  * libobs: Fix potential truncation warnings
  * libobs: WinRT and dispatcher init on graphics thread
  * libobs-winrt: Add dispatcher queue API
  * Revert "Merge pull request #2637 from kkartaltepe/cmake-variety-fixes"
  * UI: Install public headers for frontend-api
  * obs-vst: Fix crash when the blocksize is smaller than frames
  * obs-vst: Compile the vst plugin on linux
  * UI: Fix wrong path in the crash message dialog
  * UI: Swap to new srt output
  * obs-ffmpeg: Use obs-ffmpeg-mux for mpegts network output
  * obs-ffmpeg: Move file read error to separate function
  * UI: Fix GetUnusedSceneCollectionFile filename creation
  * UI: Make select/deselect signals work w/ group items
  * obs-ffmpeg: Enable mpegts network URL for ffmpeg-mux
  * UI: Allow drag & drop reorder of property lists
  * UI: Fix bug where stats dock steals focus of main windows
  * UI: Hide script tabs if no python settings
  * obs-x264: Log ignored options
  * obs-x264: Log only options given to libx264
  * obs-x264: Refactor tokenizing of options
  * win-capture: Ignore cloaked windows
  * obs-qsv11: Enable VDEnc on ICL+
  * obs-qsv11: Add latency mode to QSV settings
  * UI: Log monitoring type for global audio devices
  * libobs-winrt: Fix WGC minimize handling
  * libobs: Return target instead of current in calc_torquef
  * win-capture: Reset WGC fail flag for new window
  * cmake: Add cmake folders
  * win-capture: Fail on unsupported Vulkan formats
  * UI: Restore theme if settings window exit with [x]
  * frontend-tools: Automatically select scripts
  * libobs: Remove log entry for CoInitializeEx pass
  * libobs/util: Fix POSIX event bugs
  * libobs: Fix da_reserve early return logic
  * mac-capture: Use resize instead of reserve
  * CI: Add all-in-one macOS build script
  * win-capture: Log window capture method
  * UI: Match Windows taskbar state to tray icon
  * libobs-winrt: win-capture: Detect GraphicsCaptureItem closure
  * CI: Update Github Actions with caching and macOS improvements
  * obs-ffmpeg: Fix AVFrame handling in FFmpeg output
  * UI/updater: Fix launching OBS as admin post-update
  * deps/glad: Fix build with GCC-10
  * vlc-video: Allow metadata retrieval through proc_handler
  * rtmp-services: Update Switchboard Live servers
  * rtmp-services: Add Xlovecam.com streaming service
  * libobs: Use SetThreadDescription if possible
  * libobs: Fix unnecessary duplication
  * UI: Remove unused variable
  * libobs: Update version to 25.0.8
  * libobs-opengl: Lock Mac parent context during present
  * plugins: Add oss-audio plugin
  * libobs: Add Windows 10 release version to crash log
  * obs-ffmpeg: Update error message in process_packet
  * text-freetype2: Add Enable Antialiasing option
  * rtmp-services: Update GameTips.TV
  * obs-text: Add Enable Antialiasing option
  * obs-scripting: Expose platform functions to scripts
  * obs-plugins: Check if sources are showing for media hotkeys
  * vlc-video: Enable building the plugin on FreeBSD
  * libobs: add ppc64(le) specific flags to libobs.pc
  * rtmp-services: Add Nimo TV
  * linux-capture: Add support for cropping input source
  * libobs: Don't check filter compatibility on not loaded sources
  * UI: Remove first run auto-config prompts
  * libobs: Don't allow duplicating scene sources
  * UI: Highlight unknown audio device label in settings
  * UI: sort audio sources by name locale aware
  * obs-filters: 3D LUT tetrahedral interpolation
  * UI: Add button to Analyzer in the Log Reply window
  * UI: Add description to Log Reply window
  * UI: Differentiate between crash & session log dialogs
  * UI: Hide Help icon in Log Reply window
  * libobs: Implement and use better scaling function for 64-bit integers
  * cmake: Fix warnings and normalize variables/errors
  * obs-ffmpeg: Rename and add more VAAPI levels
  * obs-ffmpeg: Expose VAAPI profile choices
  * win-capture: Verify VK_KHR_external_memory_win32 support
  * win-capture: Cleaner COM usage
  * win-capture: Use VkAllocationCallbacks
  * UI: Remove language region
  * UI: Use standard resolutions with auto-config
  * libobs-opengl: Support 3D texelFetch
  * obs-filters: Implement CUBE LUT domain properly
  * UI: Don't clip meters when resizing with no input
  * UI: Fix buttons changing minimum window width
  * media-playback: Unbuffered Media Source
- Remove c7f84f8fc4e90ef779a204ac268f5ee1a962e324.patch.
* Wed Jul  8 2020 Jimmy Berry <jimmy@boombatower.com>
- Add c7f84f8fc4e90ef779a204ac268f5ee1a962e324.patch to resolve
  gcc10 build failure.
* Mon Apr 27 2020 jimmy@boombatower.com
- Update to version 25.0.8:
  * Revert "Merge pull request #1786 from brittneysclark/qsv_texture_based_encoding"
  * libobs: Update version to 25.0.8
  * CI: Update macOS deps to fix lua
  * obs-ffmpeg: Add error message for non-zero GPU
  * obs-ffmpeg: Add localization for NVENC error messages
  * libobs: Clear last error on encoder shutdown
  * obs-ffmpeg: Preserve error message from new NVENC
  * obs-ffmpeg: Log why new NVENC might not be used
  * UI: Remove requirement for replay buffer hotkey
  * obs-filters: Add a user label to the LUT filter
  * CI: Fix Azure Pipelines macOS runs
  * obs-browser, obs-vst: Fix formatting
  * UI: Update OSX to macOS in English translation
  * rtmp-services: Add VirtWish service
  * rtmp-services: Change Stripchat streaming service
  * UI: Add white icons for dock titles
  * Revert "UI: Remove unnecessary global variables"
  * libobs-opengl: Fix viewport flip
  * CI: Add main Github Actions workflow for branch pushes and PRs
  * UI: Remove unnecessary global variables
  * UI: Adjust a few margins
  * obs-vst: Fix formatting
  * obs-browser: Fix formatting
  * UI: Remove all scenes in ClearSceneData
  * libobs: Don't save removed sources
  * rtmp-services: Update ChathostessModels service (#2745)
  * obs-qsv11: Enable QSV texture-based encoding
  * libobs: Fix plugin folder search path case on macOS
  * UI: Add status icons for recording and streaming
  * CI: Add freetype dep on osx
  * rtmp-services: Add WASDTV (#2697)
  * docs/sphinx: Add Property Grouping
  * libobs: Update version to 25.0.6 (mac release)
  * obs-vst: Don't allow widget close on macOS
  * CI: Add qt5-xml package for FreeBSD build task
  * linux-jack: Fix conversion from channels to speaker layout
  * obs-ffmpeg: Fix media source not closing file when inactive
  * UI: Refuse drop operations from our own widgets
  * UI: Fix projector on other than primary display
  * linux-v4l2: Fix build with Clang 10.0
  * obs-ffmpeg: Add error text for NVENC AVERROR_EXTERNAL
  * obs-ffmpeg: Use new encoder error handling functions
  * libobs: Add support functions for encoder error handling
  * mac-syphon: Move the syphon plugin over to ARC
  * CI: Rewrite new deps paths in obs-ouputs.so
  * CI: Move clang format check into a seperate github workflow
  * UI: Fix warning when compiling with Clang 10
  * UI: Properly apply hide cursor on fullscreen projectors
  * rtmp-services: Add niconico
  * rtmp-services: Update castr.io rtmp ingest list
  * UI: Fix missing includes
  * libobs: Update version to 25.0.5 (mac release)
  * libobs-opengl: Fix atan2 HLSL->GLSL transpile
  * libobs-opengl: Add sincos to HLSL->GLSL transpile
  * obs-browser: Fix formatting
  * libobs/util: FreeBSD/Dragonfly exec path support
  * UI: Log global audio devices and their filters
  * CI: Update dependencies on macOS
  * mac-capture: update owner_pid in `update_window`
  * mac-capture: Use int in place of NSNumber for owner_pid
  * deps: lzma: also use .note.GNU-stack on FreeBSD
  * mac-capture: Only find window by window id when owner name and pid match
  * mac-capture: Use window id to identify windows on MacOS
  * plugins: Build ALSA plugin for FreeBSD
  * UI: Fix previewLabel styling
  * obs-outputs: Fix warnings WITH_RTMPS=OFF
  * UI: Require selected source for Transform shortcut
  * CI: Update macOS dependencies
  * rtmp-services: Fix memory leak when update rtmp-custom-service.
  * CI: Make processor count consistent
  * rtmp-services: Update Bongacams servers and settings
  * UI: Don't open Studio Mode's Program label in a window
  * CMake: Build Windows modules with file descriptors
* Sun Apr  5 2020 jimmy@boombatower.com
- Update to version 25.0.4:
  * libobs: Update version to 25.0.4
  * win-capture: Update graphics hook version to 1.1.4
  * UI: Don't stretch server field in Qt 5.14
  * obs-browser: Fix interact keyboard input on Linux
  * Decklink: Fix crash when no matching device
  * libobs: Fix macOS 10.15 hotkey crash (temporary)
  * win-capture: Fix crash if GPU can't Vulkan capture
  * docs/sphinx: Bump major OBS version
  * UI: Use Qt dialogs for Font & Color Pickers on Linux
  * obs-qsv11: Fix QuickSync LA_ICQ encoder settings
  * rtmp-services: Remove executable bits from json files
  * obs-ffmpeg: Expose old NVENC on Windows 7
  * UI: Fix text handling for dialogs
  * libobs-winrt: Stronger exception handling
  * UI: Fix silent scenes with imported SL scenes
* Tue Mar 24 2020 jimmy@boombatower.com
- Update to version 25.0.3:
  * libobs: Update to 25.0.3 (linux hotfix once again)
  * linux-v4l2: Fixup invalid id
  * libobs-d3d11: Log device PCI IDs
  * obs-outputs: Fix mbed TLS build issues
* Mon Mar 23 2020 jimmy@boombatower.com
- Update to version 25.0.2:
  * linux-v4l2: readonly controls cause infinite loop
  * libobs: Update version to 25.0.2 (linux hotfix)
  * UI: Set correct window title for fullscreen projector
  * CI: Update Linux CI from Ubuntu 16.04 to 18.04
  * UI: Make links in updater clickable
  * obs-filters: Fix LUT file extension filter on Linux
  * win-wasapi: Fix leaking IPropertyStore
  * win-wasapi: Fix crash on certain devices
  * obs-qsv11: Fix target usage values
  * UI: Fix crash on settings update
  * libobs: Add move assignment operator for BPtr
  * libobs: Fix missing assignment operator return
  * libobs: Fix size mismatch warning
  * libobs: Handle noexcept warnings
  * UI: Make Importer destructor virtual
  * UI: Add setting for Mixer add-on choice
  * linux-capture: Use RandR monitors for screen information
* Thu Mar 19 2020 jimmy@boombatower.com
- Update to version 25.0.1:
  * libobs: Update version to 25.0.1
  * libobs-winrt: Fix missing parentheses
  * UI: Fix memory leak
  * Revert "win-capture, libobs: Show names of displays in Display Capture"
  * obs-browser: Fix a few crashes
  * UI: Fix preview state when minimizing to tray
  * UI: Remove unnecessary vertices for preview
  * UI: Get actual projector monitor name on windows
  * obs-ffmpeg: Make sure to show FFmpeg NVENC on non-windows
  * libobs-winrt: Catch more hresult exceptions
  * win-capture: Retry with last known window if first fails
  * UI: Restart when browser hardware acceleration changed
  * libobs-winrt: win-capture: Clean up error handling
* Wed Mar 18 2020 jimmy@boombatower.com
- Update to version 25.0.0:
  * win-capture: Fix potential crash due to unhandled exceptions
  * libobs: Update version to 25.0.0
  * Update translations from Crowdin
  * rtmp-services: Add getloconow
  * rtmp-services: Fix formatting
  * UI: Fix closing OBS before showing whats new dialog
  * obs-browser: Fix crash with certain settings combo
  * libobs: Fix audio not playing back with audio lines
  * UI: Enable BTTV login popup
  * UI: Turn off T-bar mode when going out of studio mode
  * libobs: Reset manual state when forcing transition target
  * Revert "libobs: Add extra reference when source is displayed"
  * Revert "libobs: Only manipulate input source ref counts"
  * win-capture: Destroy winrt in graphics thread
  * libobs: Remove repeated semicolons
  * libobs: Add task scheduling features
  * UI: Increment filter name automatically
  * UI: Update stream key link for YouStreamer
  * libobs: Fix another group id comparison
  * Make cert revocation check fails non-fatal on Win
  * win-capture/graphics-hook: Separate some debugging stuff
  * win-capture: Vulkan surface refactor
  * UI: Support Unicode for Windows fullscreen projectors
  * UI: Fix filter rename crash
  * UI: Update Contribute link in about box
  * libobs: Check return value from obs_scene_add_internal
  * UI: Fix preview scaling on scene collection change
  * obs-vst: Fix lockup/race on shutdown
  * Revert "graphics: libobs-d3d11: Use DXGI_SWAP_EFFECT_FLIP_DISCARD on Windows 10"
  * win-capture/graphics-hook: Add a bit of logging
  * win-capture: Handle vkCreateSwapchainKHR errors
  * libobs: Remove legacy libobs data search path
  * libobs: Remove legacy module search path
  * win-capture: Try window handle 0 if actual handle fails
  * win-capture: Use full app obj name for keepalive mutex
  * libobs: Don't render audio if context not initialized
  * libobs: Fix groups not being recognized as groups
  * libobs: Handle removed plugins for versioned sources
  * libobs: Don't return false, return NULL
  * libobs: Fix crash when querying versioned id
  * tests: fix missing parameter when calling obs_display_create
  * win-capture/graphics-hook: Make vulkan layer all capital
  * libobs: Fix source type versioning system
  * image-source: Don't use video info for color source size
  * libobs: Compare scene/group ids by strcmp
  * win-capture: Increment graphics hook version
  * win-capture/graphics-hook: Fix reacquire bug
  * win-capture: Always copy file when debugging
  * win-capture/graphics-hook: Log vulkan capture dimensions
  * UI: Fix windowed multiview title
  * obs-scripting: Add missing Python imports
  * win-capture, libobs: Show names of displays in Display Capture
  * UI: Show monitor names for projectors
  * win-capture: Allow write permission on graphics hook
  * win-capture: If elevated, replace HKCU reg entry with HKLM
  * win-capture: Remove SYNCHRONIZE permission
  * libobs-winrt: win-capture: HDC cursor capture for WGC
  * win-capture: Restore Vulkan 1.1 version hack
  * win-capture: Support VK_FORMAT_A8B8G8R8_UNORM_PACK32
  * obs-ffmpeg: Make sure hotkeys are actually pressed
  * win-capture/graphics-hook: Fix wrong HWND
  * win-dshow: Fix rotation not working in all cases
  * win-capture: Set ALL APPLICATION PACKAGES perms if elevated
  * UI/updater: Add perms for ALL APPLICATION PACKAGES
  * win-capture: Remove microsoft store from capture blacklist
  * linux-v4l2: Use LP64 macro to determine pointer size
  * win-capture: Vulkan capture clean-up
  * win-capture: Clean up various VC++ warnings
  * obs-outputs: Fix RTMP authentication
  * win-capture: Fix format string warning
  * win-capture: Increment graphics hook version
  * libobs: Only manipulate input source ref counts
  * win-capture: Handle NULL VkApplicationInfo
  * UI: Fix override transition not working
  * UI: Do not disable t-bar
  * UI: Fix scenes as sources for SL import
  * UI: Lower minimum dock size
  * win-capture: Find correct window even if it's minimized
  * CI: macOS use qt 5.14.1
  * obs-ffmpeg: Fix some incorrect settings for srt output
  * UI: Remove unused variable
  * UI: Call setWindowFlags before setupUi
  * UI: Fix importing SL collections with repeated names
  * obs-browser: Fix CEF initialization conflict
  * UI: Dynamically set widget index when renaming sources
  * CMake: Disable incremental linking on Windows
  * win-capture: Disable correct capture method index
  * CMake: Enable /OPT:REF for Windows
  * CI: Remove merge conflict bot for now
  * CI: Fix some macOS build settings
  * win-capture: Prevent WGC being selected when unavailable
  * UI: Move OBSBasicSettings to scoped block
  * UI: Don't add removed sources when refreshing LoadAudioSources
  * UI: Use invokeMethod to refresh LoadAudioSources
  * UI: Fix preview not being re-enabled on maximize
  * win-dshow: Add support for devices that relay rotation
  * libobs: Add ability to rotate async sources
  * UI: Show help icon for properties with tooltips
  * obs-ffmpeg: Fix type conversion warning
  * win-capture: Fix registry lookup bug
  * win-capture: Check hook version before capture init
  * win-capture: Add Vulkan capture
  * win-capture: Use full DLL path for inject helper
  * win-capture/graphics-hook: Don't allow multiple hooks
  * cmake: Add FindVulkan module
  * win-capture: Refactor create_hook_info
  * win-capture/graphics-hook: Refactor mutex check
  * libobs/util: Add dll version compare func
  * libobs/util: Use MAX_PATH for absolute path funcs
  * win-capture/graphics-hook: Fix OBS detection
  * win-capture/graphics-hook: Add flog and flog_hr
  * CI: Fix case of PlugIns directory
  * obs-outputs: Update FTL sdk to latest version
  * Revert "libobs: Fix audio keyframe issue"
  * obs-browser: Fix crash with replay buffer events
  * win-capture: Preserve current window setting
  * win-capture: Move window capture method below window
  * Decklink: Fix crash when no device selected
  * frontend-plugins: Refactor Decklink out UI
  * UI: Remove dock margins
  * libobs-d3d11: Enable NV12 for Intel on newer platforms
  * obs-browser: Update to 2.8.2
  * UI: Fix compiling error with older QT
  * CI: Build CEF on Linux
  * obs-browser: Enable Linux support
  * libobs: Handle empty path in os_get_path_extension
  * libobs-opengl: Fix Mac VAO created without context
  * libobs-winrt: win-capture: Support client area toggle for WGC
  * win-capture: Hide settings if Automatic is WGC
  * UI: Use deleteLater() rather than explicit delete
  * UI: Reserve correct number of elements in vector
  * cmake: Copy a few missing dependency files
  * UI: Reserve correct number of elements in vector
  * UI: Make t-bar smaller
  * obs-browser: Fix formatting
  * deps/media-playback: Fix formatting
  * obs-browser: Update browser to 2.8.0
  * libobs: Pump graphics loop one final time for cleanup
  * UI: Fix compilation warning re signed/unsigned
  * libobs/util: Retry pipe writes to avoid short-write failures
  * win-capture: Add 'auto' method to window capture
  * CMake: Add check for Win SDK 10.0.18362.0 or above
  * CMake: Rquire CMake 3.16
  * libobs-winrt: Add PCH
  * win-capture: Windows Graphics Capture support
  * libobs-winrt: Add module for WinRT functionality
  * CI: Use VS 2019 and windows-2019 VM image
  * win-capture: Add support for finding windows via EnumWindows
  * libobs: Add extra reference when source is displayed
  * libobs: Pump Win32 messages on the graphics thread
  * libobs: Support device loss registration
  * libobs: Make ComPtr header self-sufficient
  * libobs: Don't strip whitespace from config values
  * UI: Return 0 when launch cancelled or failed
  * CI: Remove unused Linux script
  * obs-outputs: Properly reset stream count on RTMP_Close
  * UI: Don't set audio encoder track index in Adv Output
  * UI: Fix Import Profile in Portable Mode
  * obs-scripting: Update text source IDs
  * UI: Allow custom browser delete button to fill the cell
  * UI: Fix table heading visibility in Acri
  * win-ivcam: Fix build issue with CMake 3.16
  * image-source: Increase slideshow limit to 400MB
  * rtmp-services: Add Whalebone.tv
  * obs-ffmpeg: Mark FFmpeg NVENC as internal
  * UI: Hide encoder if marked internal
  * UI: Allow rescaling for texture-based encoders
  * obs-ffmpeg: Fall back to FFmpeg nvenc if recale active
  * libobs: Add obs_encoder_scaling_enabled()
  * win-capture: Fix hook collisions with multiple game captures
  * decklink: Fix crash when no outputs are available
  * CI: Add github workflow to tag merge conflicts
  * UI: Fix locked sources being transformed
  * obs-vth264: Manually mark priority bits for VideoToolbox frames
  * UI: Add ability to lock volume
  * UI: Restart program when audio/locale changed
  * UI: Use OBS dock menu instead of Qt dock context menu
  * UI: Add advanced scene collection importer
  * Revert "mac-vth264: Manually mark priority bits for frames"
  * UI: Fix preview not being disabled when minimized
  * deps/media-playback: Fix buffering/sync issues
  * libobs: Remove unused variable
  * libobs: Fix audio keyframe issue
  * UI: Allow resizing docks when hotkeys are disabled
  * rtmp-services: Add Madcat
  * rtmp-services: updating castr.io rtmp ingests
  * rtmp-services: Uncanny.gg
  * obs-ffmpeg: Use callbacks when starting/ending
  * deps/media-playback: Simplify seek/time code
  * libobs: Restore order
  * CI: Fail osx and linux on build failures. Fix decklink clang-format
  * UI: Add missing function declaration
  * decklink: Fix formatting
  * decklink: Log decklink API version on plugin load
  * UI: Add Chromium-compatible NSApplication subclass
  * libobs: fix obs_sceneitem_group_XXX_item API
  * docs/sphinx: Fix missing parameter in documentation
  * libobs: Add group functions that can signal refresh
  * libobs: Make group subitem add/remove funcs signal refresh
  * UI: Watch for refresh signal in source list
  * libobs: Add refresh signal to scenes
  * docs/sphinx: Fix typo
  * libobs: Fix Mac linker error
  * docs/sphinx: add media controls
  * docs/sphinx: add source icon
  * README.rst: Remove retired CI services
  * obs-ffmpeg: Add media hotkeys
  * obs-ffmpeg: Add media control support
  * vlc-video: Add media control support
  * UI: Fix transitions being disabled
  * UI: Use absolute path for portable mode multi check
  * UI: Show source icons in Advanced Audio Properties
  * win-capture: Faster display / window capture updates
  * UI: Always prompt when updates are available
  * libobs/util: Fix incorrect assertion in darray_insert_array
  * UI: Fix incorrect parameter
  * UI: Fix incorrect parameter value
  * deps/media-playback: Fix formatting
  * obs-transitions: Halve stinger padding to 250ms
  * libobs: Add media control support to backend
  * obs-outputs: Remove hard-coded certificate paths on Linux
  * mac-capture: Fix redundant call
  * UI: Fix transtions not enabled
  * UI: Use input validator on resolution line edit
  * libobs: Add obs_scene_find_source_recursive
  * UI: Don't allow resolutions too large
  * obs-outputs: Remove server support from librtmp
  * obs-outputs: Remove unused variable
  * obs-outputs: Fix build with older mbedtls versions
  * CI: Add libmbedtls-dev
  * obs-outputs: Show UI error if the root certs don't load
  * obs-outputs: Enable logging before calling RTMP_Init
  * obs-outputs: Add additional paths for root certificates on Linux
  * obs-transitions: Set stinger media source's name
  * enc-amf: Update to 2.7.0
  * obs-outputs: Fix librtmp mbedtls thread safety
  * UI: Fix aspect ratio triggering settings change
  * UI: Fix t-bar not working with transition override
  * linux-v4l2: Mark aarch64 and mips n64 as known platform
  * libobs: Build SIMDE on platforms without SSE2
  * rtmp-services: Add Uscreen
  * libobs, obs-x264: Fix compiler warnings
  * deps/obs-scripting: Fix incorrect parameter type
  * UI: Add option to toggle source icons to View menu
  * UI: Fix Qt 5.14 deprecation warnings
  * libobs: Rename DEPRECATED to OBS_DEPRECATED
  * docs/sphinx: Add obs_group_from_source
  * docs/sphinx: Add obs_enum_scenes
  * audio-monitoring: Fix Pulse Audio crash
  * libobs: Add VIDEO_CS_SRGB enum value
  * image-source: Fix color source default size
  * rtmp-services: Update SermonAudio entry (#2324)
  * Remove Appveyor
  * obs-text: Change default size of text to 256
  * text-freetype2: Change default size of text to 256
  * image-source: Change default size to size of canvas
  * libobs: Add the ability to make sources obsolete
  * UI: Fix studio mode transition bugs
  * win-dshow: Fix upside-down RGB DIBs
  * UI: Support DnD overlay in linuxbrowser
  * UI: Add drag and drop for URLs
  * UI: Make dropped HTML files use canvas size
  * obs-filters: Add Cube LUT samples
  * obs-filters: Add Cube LUT file support
  * libobs: Add basic support for half floats
  * libobs-opengl: Fix missing GL_HALF_FLOAT usages
  * librtmp: Allow partial success for mbedtls
  * UI: Fix audio restart message not hiding
  * UI: Display aspect ratios in video settings
  * media-playback: Add functions to pause/seek media source
  * docs/sphinx: Fix obs_property_list_item_disable entry
  * obs-outputs: Fix mbedtls use of deprecated functions
  * rtmp-services: Update/remove services
  * UI: Upgrade stream key link to button in Wizard
  * libobs: Log windows release version
  * libobs: Find windows version
  * UI: Fix QResizeEvent leaks
  * mac-vth264: Fix encoder list leak
  * CMake: Fix build on ppc64
  * libobs-opengl: Fix volume texture leak
  * obs-ffmpeg: Fix VC++ warnings
  * obs-scripting: Add Python functions for frontend events
  * libobs-d3d11: Don't allow volume render targets
  * libobs-opengl: Don't allow volume render targets
  * UI: Supply Windows manifest file
  * UI: Properly inform user if recording path is invalid
  * rtmp-services: Add show-it.tv
  * UI: Change remux file paths to OS style separators
  * libobs/UI: Support monospace font in multiline text property
  * UI: Halve width of tab in multiline text property
  * UI: Fix scene/source list item spacing
  * UI: Add t-bar to studio mode
  * libobs: Add manual transition "torque" support
  * libobs: Add manual transitioning support (T-bar)
  * UI: Add Active/Inactive status to adv audio props
  * UI: Add "Active Sources Only" option to adv audio props
  * UI: Add setThemeID to qt-wrappers
  * obs-filters: Add grayscale LUT image
  * libobs-opengl: OpenGL thread-safety on Mac
  * deps/obs-scripting: Expose matrix3 & 4 to scripting
  * UI: Fix compile issue
  * UI: Add option to use percent instead of dB
  * libobs: Fix corrupted pointers when removing properties
  * libobs-d3d11: Increase the frame queue capacity
  * linux-v4l2: Add support for controls
  * libobs: Update version to 24.0.6
  * CI: Fix QtNetwork in Mac packaging script
  * obs-filters: Use volume texture for LUT
  * libobs: Add support for volume textures
  * UI: Ensure OBS launches when theme is missing
  * obs-qsv11: Add all TargetUsage values
  * rtmp-services: Add YouStreamer
  * CI: Fix error deleting QT network framework on OSX
  * CI: Fix mbedtls id in mac deploy script
  * libobs: Null check hotkey device on macos
  * obs-browser: Disable system flash
  * UI: Add save button next to replay buffer button
  * rtmp-services: Increase FB max bitrate to 6Mbps
  * CI: Fix up QT network framework on OSX
  * CI: Fix osx executable path in plist
  * CI: Fix framework symlinks when building osx app
  * obs-ffmpeg: Enable VAAPI Rate Control
  * UI: Add Start Streaming settings check on start
  * UI: Create UI Validation Helper Class
  * libobs: Do not include unrelated flags in filter check
  * rtmp-services: Add Konduit.live
  * libobs: Update version to 24.0.5
  * CI: Don't run clang format on some submodule plugins
  * libdshowcapture: Update to latest submodule
  * UI: Allow switch to existing theme to reload
  * UI: Don't modify theme if already set
  * Decklink: Explicit casts for truncation warnings
  * libobs: Remove C99 hacks for older VC++
  * UI: Delete cookies before connecting account
  * UI: Fix bug in untested/unused function code path
  * UI: Fix source icons being shifted to the right
  * CI: Add Cirrus-CI config for FreeBSD builds
  * UI: Add Grid Mode to Scenes Widget
  * UI: Rename deprecated QPalette::ColorRole
  * UI: Fix Qt deprecation warnings
  * libobs: add missing FreeBSD #include to fix build
  * UI: Use new ffmpeg-encoded-output for non-RTMP urls
  * obs-ffmpeg: Add new ffmpeg-encoded-output
  * obs-ffmpeg: Expose ffmpeg_data_init and ffmpeg_data_free methods
  * libobs: fix building modules once installed
  * UI: Default stream / record confirm dialogs to "No"
  * deps/media-playback: Don't use interrupt cb for local files
  * deps/media-playback: Don't exit thread on AVERROR_EXIT
  * CI: Keep artifacts for PRs labelled "Seeking Testers"
  * libobs: Enable compilation on aarch64
  * libobs: Add aarch64 compatibility layer
  * win-dshow: Suppress MJPEG error spam
  * UI: Create an API for opening projector windows
  * UI: Break out the opening of a projector into a slot function
  * UI: Add source icons
  * libobs: Robust COM initialization
  * win-wasapi: Verify and balance CoInitializeEx call
  * UI: Fix wrong icon if recording stopped while paused
  * linux-capture: Fix cursor draw bug when cropping window cap.
  * UI: Fix wrong icon if recording stopped while paused
  * rtmp-services: Add scenecut=0 to mixer requirements
  * UI: Fix swap scene issue with double click mode
  * UI: Change advanced networking strings
  * UI: Add setting for Twitch chat add-ons choice
  * UI: Fix Twitch panels not using dark first time
  * obs-outputs: Log FTL during configure
  * libobs: Remove _WIN32 ifdef from enum
  * UI: Fix invalid escape sequences in regex string
  * UI: Add system tray icon to indicate when paused
  * libobs: fix new virtual key codes display
  * libobs: add missing virtual key codes for Windows
  * deps/obs-scripting: Fix formatting
  * obs-scripting: Fix Python in new MacOS .app bundles
  * obs-text: add missing locale include to fix build
  * UI: Remove help icon from Interact titlebars
  * win-dshow: Support bottom-up DIBs
  * win-dshow: Fix format switching issue
  * decklink-ui: Show the state of outputs in the decklink dialog
  * UI: Use radio buttons for FLV track selection
  * libobs: Add more X.org / Unix hotkey defines
  * obs-filters: Reload the mask image when file change is detected
  * obs-filters: Add toggle for scroll filter looping
  * libobs: Send activate and show signals to filters
  * rtmp-services: Type check apply_encoder_settings
  * obs-ffmpeg: Remove unexposed vaapi parameters
  * UI: Fix main transition being set to the quick one
  * win-capture: Fix rare crash when GL program exits
  * libobs: Fix race condition
  * CI: Use custom macdylibbundler for OSX deps
  * UI: Upgrade stream link hotlink to a button
  * rtmp-services: Add YouNow service and implement ingest lookup
  * README.rst: Add Crowdin progress badge
  * UI: Fallback to XGetWMName if XFetchName fails
  * mac-vth264: Manually mark priority bits for frames
  * git: Add VSCode working dir to .gitignore
  * UI: Fix audio bitrate not being set in simple mode
  * UI: Add fade to black in studio mode
  * rtmp-services: Add Stars.AVN.com streaming service
  * libobs: Add video info to filename formatting
  * UI: Fix desktop entry for GNOME Shell
  * Revert "Rename com.obsproject.Studio.desktop to obs.desktop"
  * UI: Add ability to change projector type
  * UI: Simplify fullscreen toggle code
  * win-wasapi: Log device sample rate when initialized
  * UI: Display Sample Rate with proper formatting
  * libobs-d3d11: Fix null input layout rebuild
  * obs-ffmpeg: use avcodec_find_best_pix_fmt_of_list
  * win-capture: Add additional exe to window capture blacklist
  * obs-ffmpeg: Use vendor and device ID for NVENC blacklist
  * UI: Fix checkable property groups
  * UI: Add stats reset hotkey
  * cmake: Use C++17 for compilation
  * UI: Don't influence headers with using namespace
  * obs-scripting: Quiet CMake SWIG warnings
  * CI: Remove dead PPA to fix Linux build failure
  * libobs: Export obs_group_from_source
  * UI: Add support for Custom Twitch Dashboard Docks
  * CI: Update scripts for reorganized OSX bundle
  * docs/sphinx: Fix various typos
  * libobs-d3d11: Use vendor ID instead of string match
  * libobs: Use proper resource paths when running from an OSX bundle
  * enc-amf: Upgrade to v2.6
  * UI: frontend api "trans. duration changed" event
  * libobs: Strict objc_msgSend support
  * rtmp-stream: Fix comparison between signed and unsigned ints
  * rtmp-services: Add ChathostessModels
  * obs-qsv11: Enable option for Custom Quantization Matrix
  * obs-qsv11: Add platform enums for KBL and ICL
  * libobs: Add gs_begin_frame for duplicators
  * obs-ffmpeg: Use av_opt_set on context instead of priv_data
  * obs-filters: Fix sharpness not being translated
  * UI: Fix issue with preview projector
  * UI: Add ability to rename filters with F2 (Return on Mac)
  * Rename com.obsproject.Studio.desktop to obs.desktop
  * Build: Added BUILD_CAPTIONS to linux build script
  * cmake: Compile option to fix libcaption linking
  * UI: Remove unused code from visibility item widget
  * libobs-d3d11: Add GPU driver version to log
  * UI: Add copy/paste of multiple selected sources
  * linux-capture: Fix bug with xshm input showing multiple 0x0 windows
  * libobs-d3d11: Log monitor names
  * libobs-d3d11: Log display refresh rates
  * obs-scripting: Link _obspython as dynamic_lookup on MacOS
  * obs-scripting: Fix python lib path on MacOS
  * obs-scripting: Fix script plugin destination path on MacOS
  * frontend-tools: output timer tab stop order
  * obs-text: text transform add start case
  * obs-text: text transform add locale
  * cmake: no -Werror-implicit-function-declaration for C++
  * libobs-opengl: Require OpenGL 3.3 instead of 3.2
  * win-capture: Remove support for feature level 9.3
  * libobs-d3d11: Remove "support" for feature level 9.3
  * win-capture: Remove unused variable from D3D12 capture
  * UI: Switch from RGBA to BGRA swap chain format
  * graphics: libobs-d3d11: Use DXGI_SWAP_EFFECT_FLIP_DISCARD on Windows 10
  * libobs-opengl: Support BGRA swap chains on Windows
  * UI: set names on scenes duplicated for Studio Mode
* Tue Dec 17 2019 jimmy@boombatower.com
- Update to version 24.0.6:
  * CI: Fix QtNetwork in Mac packaging script
  * UI: Ensure OBS launches when theme is missing
  * CI: Fix mbedtls id in mac deploy script
  * CI: Fix error deleting QT network framework on OSX
  * libobs: Null check hotkey device on macos
  * rtmp-services: Increase FB max bitrate to 6Mbps
  * CI: Fix up QT network framework on OSX
  * CI: Fix osx executable path in plist
  * CI: Fix framework symlinks when building osx app
  * obs-browser: Disable system flash
  * UI: Fix invalid escape sequences in regex string
* Fri Dec 13 2019 jimmy@boombatower.com
- Update to version 24.0.5:
  * libobs: Update version to 24.0.5
  * CI: Don't run clang format on some submodule plugins
  * Merge pull request #2010 from wanhongqing123/master
  * Merge pull request #2042 from WizardCM/custom-twitch-docks
  * Merge pull request #2183 from ratwithacompiler/macos-python-fix-2
  * Merge pull request #2085 from ratwithacompiler/macos-python-fix
  * Merge pull request #2090 from jpark37/dxgi-refresh-rate
  * Merge pull request #2089 from jpark37/dxgi-driver-version
  * UI: Delete cookies before connecting account
  * UI: Fix bug in untested/unused function code path
  * deps/media-playback: Don't use interrupt cb for local files
  * deps/media-playback: Don't exit thread on AVERROR_EXIT
  * deps/obs-scripting: Fix formatting
  * Merge pull request #2152 from Rosuav/fix-cursor-position
  * UI: Fix Twitch panels not using dark first time
  * Merge pull request #1914 from YouNow/master
  * Merge pull request #2140 from DevWolk/avn-obs
  * Merge pull request #2045 from wolf247/master
  * Merge pull request #2179 from WizardCM/remove-help-interact
  * Merge pull request #2125 from DDRBoxman/appbundle
  * Merge pull request #2168 from kkartaltepe/vaapi-profile-fix
  * Merge pull request #2148 from eulertour/master
  * Merge pull request #2146 from Fenrirthviti/recording-bitrate-fix
  * libobs: Fix race condition
  * Merge pull request #2147 from JohannMG/vscode-ignore
  * Merge pull request #2134 from WizardCM/wasapi-samplerate
  * Merge pull request #2129 from Fenrirthviti/win-blacklist-update
  * Merge pull request #2131 from jpark37/input-layout-error
  * Merge pull request #2128 from Xaymar/return-to-break
  * Merge pull request #2121 from cg2121/fix-warning
  * Merge pull request #2110 from derrod/ffmpeg-output-fix
  * Merge pull request #2106 from cg2121/fix-preview-bug
  * Merge pull request #2126 from Fenrirthviti/linux-ci-fix
  * Merge pull request #2091 from Programatic/xshm_wrong_windows
  * Merge pull request #2120 from jpark37/objc-msgsend
* Tue Oct 15 2019 jimmy@boombatower.com
- Update to version 24.0.3:
  * obs-browser: Remove "monitor by default" flag
  * Revert "libobs/audio-monitoring: Don't init until used"
  * libobs-d3d11: Fix code styling
  * libobs: Update version to 24.0.3
  * libobs-d3d11: Fix calling convention of loaded func
  * obs-browser: Only disable NetworkService on macOS
  * libobs-d3d11: Use unordered_map for duplicator collection
  * win-capture: Fix extra duplicator refs
  * UI: Fix issue where multiview doesn't update
  * libobs: Update version to 24.0.2
  * libobs-d3d11: Don't set GPU priority on Intel adapters
  * libobs/audio-monitoring: Add error logging
  * libobs/audio-monitoring: Don't init until used
  * obs-browser: Use older chromium network implementation
  * libobs-d3d11: Set maximum GPU priority
  * Exclude build dir from clang format
  * UI, libobs: Fix compiler warnings
  * Revert "UI: Remove FFZ from twitch integration"
  * UI: Remove FFZ from twitch integration
  * libobs-d3d11: Disable NV12 format support for WARP
  * obs-ffmpeg: Remove unbuffered mode from media source
  * obs-transitions: Fix stingers sometimes getting cut off
  * obs-browser: Update version to 2.7.12
  * obs-ffmpeg: Fix deadlock with nvenc lookahead
  * UI: Fix path calculation for disk space check
  * obs-ffmpeg: Do not enable hardware decoding by default
* Sun Sep 22 2019 jimmy@boombatower.com
- Update to version 24.0.1:
  * obs-browser: Fix a deadlock
  * libobs: Update version to 24.0.1
  * libobs: Add API to get last OBS version of a source
  * obs-browser: Signal whether audio active/inactive
  * UI: Hide mixer sources if audio deactivated
  * libobs: Add funcs to determine whether audio active
  * obs-browser: Turn rerouting audio off by default
  * UI: Check for null pointer
  * UI: Fix crash closing mixer dock panels
  * win-dshow: Do not allow H264 to have same priority as MJPEG
  * win-dshow: Disable HW decode in DirectShow for now
  * UI: Adjust locale name for zh-TW
* Thu Sep 19 2019 jimmy@boombatower.com
- Update to version 24.0.0:
  * obs-browser: Update translations from crowdin
  * Update translations from Crowdin
  * libobs: Update version to 24.0.0
  * libobs: Check to swap BGRX/BGRA in async filters
  * obs-browser: Map absolute to file URLs
  * UI: Fix extra browser panels always creating on startup
  * obs-browser: Fix panels not remembering last URL set
  * UI: Fix browser docks being unchecked when created
  * win-dshow: Fix color range when using FFmpeg decode
  * Revert "UI: Various screen reader fixes"
  * UI: Fix pause hotkey not working properly
  * obs-browser: Fix portable mode not saving cookies
  * obs-browser: Fix minor bug when using older CEF versions
  * UI: Disable NVENC lookahead if dynamic bitrate on
  * obs-browser: Fix browser panel visibility bug
  * CI: Update CEF on osx to 3770
  * obs-browser: Fix large local media file access
  * Revert "image-source: Set default size of color source to canvas size"
  * obs-browser: Fix build error on macOS
  * obs-browser: Fix browser panel crash
  * UI: Shut down browsers when browser docks hidden
  * UI: Refactor all browser dock classes in to one
  * UI: Various screen reader fixes
  * obs-browser: Allow users to use CEF audio instead of OBS
  * UI/updater: Fix variable type to format specifier
  * graphics-hook: Fix format specifier
  * obs-browser: Do not use WasHidden() for visibility on 3507+
  * obs-browser: Fix browser panel crash
  * libobs: Remove redundant function param and for loop
  * libobs: Make sure to offset unpause audio data
  * libobs: Fix pause cutting out video data prematurely
  * libobs: Fail pause/unpause if still waiting for them
  * libobs: Give a little extra time for pause to start/stop
  * libobs: Fix Area shaders missing for RGB output
  * obs-qsv11: Remove leftover stack variable
  * obs-ffmpeg: Fix video warnings
  * libobs: Fix video warnings
  * CI: Update Windows CEF version
  * libobs: Use correct pointer
  * libobs: Call debug marker after null check, not before
  * libobs: Don't render scene item texture if it's null
  * obs-browser: Do not process Qt events for browser source
  * libobs: Add graphics API to get graphics object pointer
  * deps/media-playback: Remove cuda for hardware decoding
  * deps/media-playback: Fix hw decode dropping last few frames
  * libobs-d3d11: Print feature level as %%x for readability
  * libobs-d3d11: Consistent exception catch parameters
  * rtmp-services: Update GameTips.TV
  * deps/media-playback: Use hwaccel with non-alpha WebM files
  * obs-browser: Ensure FPS always matches OBS
  * obs-browser: Don't signal frame begin if feature disabled
  * obs-browser: Actually fix browsers sometimes not rendering
  * libobs: Fix default mixer values
  * obs-qsv11: Do not enable b-frames on sandy/ivy bridge
  * obs-browser: Fix browser source sometimes not rendering
  * libobs: Insert sources to linked lists after creation
  * libobs: Add missing static to function
  * libobs: Fix null potential pointer dereference
  * libobs: Fix Lanczos calculations
  * libobs: Simplify bicubic weight calculations
  * obs-ffmpeg: Use NV_FAILED() instead of FAILED()
  * obs-ffmpeg: Force I-Frame when reconfiguring jim-nvenc
  * deps/media-playback: Fix memory leak
  * deps/media-playback: Fix hw accel decode crash
  * libobs: add pointer check in reset_raw_output
  * UI: Clarify dynamic bitrate support in tooltip
  * obs-x264: Do not display log messages every update
  * UI: Move "area" scale below bilinear, above bicubic
  * UI: Fix bug where FTL was using AAC instead of opus
  * obs-browser: Fix audio cutting out
  * libobs: Add audio lines
  * UI: Simplify toggle pause code
  * UI: Update tooltip when paused
  * UI: Fix inconsistency with spaces
  * UI: Add dynamic bitrate support to the UI
  * obs-outputs: Add dynamic bitrate to RTMP output
  * libobs: Mark encoders that support dynamic bitrate
  * obs-outputs: Allow changing bitrate test limit on the fly
  * obs-x264: Do not show reconfigure details in log
  * obs-ffmpeg: Allow FFmpeg NVENC to be reconfigured
  * linux-capture: Texture unbound after GS_GL_DUMMYTEX changes
  * Revert "win-capture: Don't leak dynamic library references"
  * libobs-opengl: Fix Clang warnings
  * UI: Redundant/bad casts
  * libobs-opengl: Redundant cast
  * UI: Add box select to preview
  * libobs: Fix browser source settings resetting pre-24
  * cmake: Fix SWIG deprecation warnings
  * UI: Use "-inf" for muted volume level
  * UI: Clarify extra browser dock text
  * libobs-d3d11: Disable NV12 usage for Intel
  * UI: Fix Area sample count text
  * obs-text: Fix formatting
  * libobs: Reset mixers for "monitoring only" sources
  * libobs, obs-scripting, vlc-video: Fix compiler warnings
  * UI: Fix compiler/Acri warnings
  * win-wasapi: Fix typo with description
  * libobs: UI: Add Area scaling for downscale output
  * libobs: Remove unnecessary divides from Lanczos
  * libobs: Fix dark lines using Lanczos
  * UI: Change Connect Account to Recommended
  * libobs: Merge obs_source_process_filter_(tech_)?end functions
  * libobs: Fix apply_settings & remove_by_name for groups
  * UI: Fix look of extra panels trash icon
  * obs-browser: Update to 2.6.1
  * libobs-opengl: Fix gl_error_to_str
  * libobs-opengl: Fix DUMMY textures left bound
  * Revert "libobs-opengl: Add GS_RGBX format"
  * linux-capture: Revert GS_RGBX usage
  * deps/media-playback: Convert YUV alpha formats to RGB on GPU
  * obs-ffmpeg: Add YUV alpha formats for completeness
  * libobs: Add YUV alpha formats
  * deps/media-playback: Add missing header to CMake
  * UI: Rename Mixer to Audio Mixer
  * libobs: Separate textures for YUV input
  * obs-scripting: Use a recursive mutex for Lua scripting
  * UI: Add the ability to create custom browser docks
  * UI: Add LineEditChanged and LineEditCanceled
  * obs-browser: Fix a few panel issues
  * libobs: Fix stale format in async frame cache
  * UI: Fix pause button checked color with Rachni theme
  * obs-scripting: Add pause scene script
  * UI: Remove Twitch from MultichannelWarning message
  * libobs: Add missing pixel format to format_is_yuv and get_video_format_name
  * win-dshow: Use unbuffered by default for MJPEG
  * win-dshow: Clarify function name/purpose
  * libobs, obs-ffmpeg, win-dshow: Fix FFmpeg 4.0 deprecation
  * win-dshow, obs-ffmpeg: Add hardware decoding support
  * libobs: Add GPU timestamp query support
  * UI: Partially revert PR #1979
  * UI: Fix Lanczos label with correct sample count
  * libobs: Separate textures for YUV output, fix chroma
  * CI: Only download Qt if it doesn't exist already
  * libobs: Optimize lanczos shader, remove scaling
  * obs-browser: Update to 2.5.0 (audio capture support)
  * libobs: Add "monitoring by default" source cap
  * libobs: Optimize bicubic shader
  * libobs: Default sampler sometimes unset for GL
  * libobs: Fix benign typo
  * win-dshow: Use FFmpeg for MJPEG decompression
  * libobs: obs-ffmpeg: win-dshow: Planar 4:2:2 video
  * UI: Pass QColor as reference
  * win-capture: Don't leak dynamic library references
  * libobs: Don't leak dynamic library references
  * libobs: Return NULL if there is no get_properties callback
  * win-wasapi: Catch by reference
  * UI: Catch by reference
  * libobs-d3d11: Catch be reference
  * libobs: Supress clang-tidy warning clang-tidy-cert-flp30-c
  * UI: Stop recording when disk space is low
  * libobs-opengl: Remove unused VERTEXID code
  * libobs-opengl: Support gl_FragCoord and cull unused interpolants
  * libobs-opengl: Fix GS_R8G8 values
  * UI: Add links for Facebook stream key
  * obs-transitions: Fix suffix with stinger transition
  * UI: Add ability to disable hotkeys when not in focus
  * UI: Fix param logic of ResetHotkeyState calls
  * libobs: Rework RGB to YUV conversion
  * libobs: Remove YUV transformation on CPU
  * UI: Fix hotkeys working even when disabled in focus
  * UI: Add option to warn on stop recording
  * UI: Improve look of adv audio control dialog
  * UI: Add Restream.io link to stream key page
  * UI: Add Restream.io bandwidth test stream key param
  * UI: Add channels widget to Restream.io integration
  * UI: Declare missing overrides
  * cmake: Fix typo
  * obs-text: Use array type for unique_ptr uint8_t[]
  * rtmp-services: Remove redundant null checks
  * libobs: Improve timing of unbuffered deinterlacing
  * win-dshow: Update libdshowcapture to 0.6.1
  * UI: Display infinity symbol when volume is at 0 percent
  * rtmp-services: Add Stripchat streaming service
  * obs-qsv: Enable high profile for QSV H.264
  * obs-qsv: Remove check for AsyncDepth in InitParams
  * libobs: UI: Remove DrawBackdrop() to save fullscreen pass
  * UI: Set default maximum name length to 170 characters
  * frontend-tools: Make start/stop buttons checkable
  * UI, obs-plugins: Add spinbox suffixes where necessary
  * libobs: obs-filters: Area upscale shader
  * file-updater: Use transparent HTTP compression
  * frontend-tools: Add option to pause output timer when rec is paused
  * obs-qsv: Enable LA_CBR as QSV rate control
  * libobs-opengl: Fix glGetError() infinite loop
  * UI: Simplify resize output code
  * obs-browser: Fix CEF 75.0.13 support
  * libobs: Fix formatting
  * UI: Add enable preview button
  * rtmp-services: Add Steam
  * obs-qsv: Enable Content Adaptive Quantization
  * obs-qsv: Enable B-frames and B-pyramid for encoder
  * CI: Run clang format on linux and osx CI and fail if changes are made
  * libobs: Call both get_defaults and get_defaults2
  * UI: Fix toggled signal of property groups
  * libobs: Fix formatting
  * obs-qsv: Add newer platforms to CPU enum
  * UI: Make Dark theme group box title bold
  * linux-v4l2: Add "Default" color range setting
  * win-dshow: Add "Default" color range setting
  * UI: Change default recording format to MKV
  * Apply clang-format to objective c code
  * obs-ffmpeg: Separate logging code
  * libobs: Clear module variable in case module reloaded
  * linux-capture: Fix xcompcap robustness
  * libobs-opengl: Fix GS_GL_DUMMY textures creation
  * libobs-opengl: Add GS_RGBX format
  * libobs-opengl: Add error enum to string function
  * UI: Add pause support
  * obs-ffmpeg: Add support for pausing
  * libobs: Implement pausing of outputs
  * obs-ffmpeg: Remove unnecessary function
  * libobs: Correct raw output starting audio data
  * libobs: Add obs_get_frame_interval_ns
  * UI: Don't display MP4/MOV warning if lossless
  * obs-ffmpeg: Check for replay buffer button press
  * UI: Make adv. streaming audio encoder independent
  * libobs: Buffer-smoothing enhancements
  * win-dshow: Decouple audio from video
  * rtmp-services: Update and prune services
  * libobs-d3d11: Set texture using initializer list
  * obs-outputs: Minor pointer fixes
  * UI: Avoid ternary operator for mixed types
  * libobs: Fix format selection
  * libobs-d3d11: Unnecessary type conversions
  * .git-blame-ignore-revs: Add file to handle mass reformatting
  * clang-format: Remove redundant params
  * rtmp-services: Update ingest list for Restream.io
  * obs-text: fix text transform on updated file
  * libobs-opengl: Empty VAO
  * libobs-d3d11: Fix missing vertex buffer clear in NV12 check
  * obs-ffmpeg: Move external headers to external dir
  * clang-format: Apply formatting
  * clang-format: Add clang-format files
  * cmake: Install 'libobs.pc' under the correct 'libdir'
  * libobs: Full-screen triangle format conversions
  * UI: Use stream track if no tracks are selected
  * Revert "UI: Use theme colors setting for Projectors too"
  * libobs, UI: Implement item_locked event
  * libobs-d3d11: Clean up device_projection_pop
  * libobs: Area-resampling shader optimizations
  * libobs: linux-v412: obs-ffmpeg: Add packed BGR3 video support
  * libobs: Remove unnecessary frame pipelining
  * libobs: Improve low-resolution bilinear sampling
- Upstream moved pkgconfig/libobs.pc to libdir for x86_64.
* Mon Jun 17 2019 jimmy@boombatower.com
- Update to version 23.2.1:
  * libobs: Update version to 23.2.1
  * obs-frontend-api: Add func to add custom docks
  * libobs: Disable blending when converting sources
  * UI: Fix editor inheriting source list stylesheet
  * UI: Fix bug with custom source list item color
  * UI: Fix tray icon showing up on startup even if off
  * libobs: Fix null pointer dereference
* Thu Jun 13 2019 Jimmy Berry <jimmy@boombatower.com>
- Update %%post script for new desktop file name.
- Include appdata in files list.
- Include obs-ffmpeg-mux in files list.
* Thu Jun 13 2019 jimmy@boombatower.com
- Update to version 23.2.0:
  * libobs: Update version to 23.2.0
  * Update translations from Crowdin
  * UI: Make two-auth message a bit friendlier
  * UI: Use better link for Twitch two-factor warning
  * win-capture: Add discord to game capture blacklist
  * UI: Fix transition A/B labels on macOS/Linux
  * UI: Add two-factor authentication warning for Twitch
  * UI: Add ability to use rich text in warning dialogs
  * UI: Fix output icon size. Add padding to settings list items
  * UI/updater: Update some text for clarity
  * UI/updater: Add marquee progress bar for existing file check
  * UI/updater: Add manifest file for DPI awareness
  * UI: Revert Dark theme Scenes font change
  * CI: Fix travis test on OSX
  * CI: Build CEF with OS X 10.11 target
  * UI: Ensure frontend event is removed on object deletion
  * win-wasapi: Speaker enum fixes
  * UI: Fix "Toggle Preview" hotkeys duplicating
  * GitHub: Add funding buttons
  * libobs-d3d11: Bad indices in log output
  * libobs: Pair encoders only when output actually starts
  * UI: Fix issue where rec time left would show negative time
  * libobs: Remove unreachable YUV decode paths
  * obs-filters: Remove unused key_rgb shader variable
  * obs-filters: Remove unused variable for color key
  * libobs: Remove saturate from RGB -> YUV conversion
  * UI: Remove unused helper function renderVB
  * obs-browser: Close browser panels early
  * UI: Remove 5 file limit for drag & drop
  * libobs: Fix lockup when an encode call fails
  * UI: Dark theme consistency for Scenes vs Sources
  * UI: Remove unused hotkey qss items
  * UI: Fix theme issues with hotkey icons
  * UI: Add hover color to hotkey icons
  * UI: Add Transition Previews
  * libobs: Add transition and showing counter functions
  * README.rst: Add contributing/donating link
  * obs-ffmpeg: Fix VAAPI CBR
  * libobs: UI: Remove Qt usage from graphics thread
  * obs-outputs: Fix undefined MSG_NOSIGNAL
  * libobs: Restore casts to fix Clang warnings
  * obs-qsv: Update libmfx, fix QSV with new DCH drivers
  * UI: Block SIGPIPE in all threads
  * obs-outputs: Return error instead emitting SIGPIPE
  * obs-frontend-api: Add func to trigger a Studio Mode transition
  * obs-frontend-api: Add methods to get/set transition duration
  * libobs: Fix various alpha issues
  * UI: Change fader type to log
  * UI: Make volume faders more precise
  * UI: Change volume to dB in adv audio properties
  * UI: Use escaped html for about dialog
  * UI: Add Patreon contributors to About dialog
  * win-dshow: fix issue decoding some H.264 stream
  * UI: Fix system tray not working
  * UI: Hide Alpha channel field from the color picker
  * UI: fix crash due to NULL dereference
  * rtmp-services: Update GameTips.tv
  * libobs: Fix crashes from wrong types
  * CI: Use swig 3.0.12 on OSX
  * UI: Fix theme showing incorrect theme when on Dark
  * CI: Use swig 3.04 on OSX
  * obs-ffmpeg: Fix jim-nvenc initial DTS for fractional FPS
  * UI: Add ability to set properties spinbox suffix
  * libobs: Add ability to set spinbox property suffix
  * UI: Use icons for hotkey buttons
  * UI: Truncate text in hotkeys interface
  * UI: Remove icons from settings button box
  * UI: Improve look of Dark theme
  * UI: Remove settings horizontal lines
  * UI: Remove mac browser workarounds, improve stability
  * UI: Only execute "What's New" code on win32
  * UI: Check for valid systen tray pointer
  * UI: Increment bitrates by 50
  * libobs: Use RTLD_FIRST when loading libraries on macOS
  * UI: Fix theme issues with vis/lock checkboxes
  * obs-ffmpeg: Move ffmpeg-mux to executable dir
  * libobs/util: Add function to get executable path
  * obs-filters: Use int sliders for opacity
  * obs-filters: Fix opacity on image mask/blend filter
  * libobs: Support limited color range for RGB/Y800 sources
  * decklink, win-dshow: Use obs_source_output_video2
  * libobs: Add better default source color range handling
  * Revert "libobs: libobs-d3d11: obs-filters: No excess alpha"
  * UI: Fix theme bug when updating from older versions
  * UI: Add ability to copy/paste scene filters
  * UI: Fix unable to escape when renaming scene
  * UI: Fix group checkbox icons not working in Dark theme
  * UI: Simplify locked/visibility checkboxes
  * UI: Change icons to svg
  * UI: Fix preview/program label alignment
  * libobs: Fix GS_UNSIGNED_LONG definition
  * obs-outputs: Fix leak with certs for rtmp
  * UI: Rename UI files for consistency
  * UI: Fix whitespace issues with "ignore wheel" widgets
  * UI: Do not remove focus on mouse leave events
  * win-wasapi: Unapply/reapply audio monitoring on reconnect
  * win-wasapi: Fix audio capture after unplugging device
  * win-wasapi: Call CoInitializeEx in reconnect thread
  * decklink-output-ui: Fix memory leak
  * rtmp-services: Update Mixer keyframe interval
  * UI: Do not allow mouse wheel for volume slider
  * libobs: UI: Fix rotated line scale
  * obs-ffmpeg: Add logging of last error for passing to UI
  * libobs: Allow Win32 pipes to pass STDERR for logging of errors
  * UI: Update error message severity levels and show additional info
  * UI: Add warning / critical QMessageBox wrappers
  * Use proper capitalization for string
  * UI: Add support for property groups
  * libobs: Add property groups
  * Decklink: inital preview out work
  * UI: Use theme colors setting for Projectors too
  * UI: Correct custom property implementation
  * vlc-video: Enable subtitle track selection
  * UI: Add default color for the preview background
  * UI: Fix Linux build without PulseAudio
  * UI: Estimate recording time left until disk is full
  * libobs: Fix shader for GLSL
  * UI: Add Linux AppStream metadata
  * UI: Add hotkey to toggle preview
  * win-capture/graphics-hook: Check if mutex abandoned
  * UI: Remove SourceListWidget
  * UI: Ignore wheelEvent for properties
  * rtmp-services: Add OnlyFans streaming service
  * CONTRIBUTING.rst: Improve commit guidelines
  * UI: Fix remux dialog ignoring filename changes
  * UI: Separate delegate class into header file
  * UI: Show a message in the empty source list
  * deps/media-playback: YUV444P support
  * libobs: Simplify YUV conversion
  * UI: Add null check for rename of default theme
  * UI: Don't hide cursor over multiview
  * UI: Add ability to center items vertically/horizontally
  * UI: Rename Default theme to System
  * libobs: Add additional effect debugging information
  * Remove double spaces from localization
  * UI: Fix size of output icon
  * vlc-video: Enable audio track selection
  * UI: Add text autoselect for source rename
  * UI: Add text autoselect on scene rename
  * libobs: UI: Use graphics debug markers
  * libobs/graphics: Support debug markers
  * libobs: Fix move assignment operator for ComPtr
  * libobs: libobs-d3d11: obs-filters: No excess alpha
  * UI: Don't update stats dock if hidden
  * UI: Fix bandwidth test flag being saved to stream key
  * cmake: Generate obs.rc out-of-tree
  * libobs: Add function to remove properties
  * linux-capture: Add randr support
  * obs-frontend-api: Access system tray icon from API
  * UI: Fix incorrect padding usage in Rachni theme
  * UI: Show correct version in about dialog
  * UI: Log group items on startup
  * UI, libobs, text-freetype2: Add missing pragma once in header files
  * libobs: Add support for F25-F35 hotkeys on Linux
  * UI: Hide border for Output Settings container
  * UI: Hide border for General Settings container
  * UI: Refactor Audio Settings tab structure
  * plugins: Clear all compiler warnings
  * libobs: Clear all compiler warnings
  * UI: Fix Q_PROPERTY compiling warnings
  * libobs-opengl: Clear some conversion and uncaught switch cases warnings
  * image-source: Set default size of color source to canvas size
  * CI: Build caption output support on OSX by default
  * deps/obs-scripting: Expose obs_output_output_caption_text1 to scripts
  * Improve locales
  * obs-filters: Add luma key filter
  * libobs: Add minimum display duration to caption data
  * UI: Show output's last error in failure dialog
  * libobs: Initialize service before starting output
  * UI: Fix unencoded stream failure
  * obs-ffmpeg: Bind network buffer size in the UI
* Sat Apr  6 2019 Jimmy Berry <jimmy@boombatower.com>
- Add libqt5-qtsvg-devel as a build dependency.
* Sat Apr  6 2019 jimmy@boombatower.com
- Update to version 23.1.0:
  * obs-ffmpeg: Remove "A" variants from NVENC blacklist
  * libobs: Fix and simplify Area scale filter
  * Update translations from Crowdin
  * libobs: Update version to 23.1.0
  * UI: Do not show [x] (close) for primary dock widgets
  * UI: Fix file browser showing up when dir selected
  * UI: Fix issue where space/esc hotkeys would be blank
  * UI: Fix crash when using ctrl-c in Linux terminal
  * UI: Allow smaller Restream docks
  * libobs, image-source: Fix ABI break in image_file_t structure
  * UI: Fix act. feed version hide check to <= 23.0.2
  * libobs: Change internal version to 23.0.3 (temporarily)
  * obs-ffmpeg: Show encoder name when logging jim-nvenc
  * UI: Hide act. feed by default if prev ver below 23.1
  * UI: Remove help icon from source select dialog
  * UI: Don't open settings or close in event subloop
  * libobs: Update version to 23.1.0
  * CI: Add Restream secrets for AppVeyor
  * obs-ffmpeg: Fix blacklisted adapter check
  * UI: Add Restream integration
  * win-dshow: Update libdshowcapture for crash fix
  * libobs: Remove dead code in sharpness effect
  * obs-filters: Remove unused function in shader
  * libobs: Fix Area scale filter for GLSL
  * CI: Don't build service integration in PRs&Forks
  * CI: Build service integration on Azure Pipelines
  * obs-browser: Make DispatchJSEvent asynchronous
  * libobs: Fix ABI break
  * UI: Remove and ignore obs.rc
  * libobs-opengl: Fix bad log string
  * libobs: Fix output type specifiers
  * libobs: Fix invalid max_anisotropy value
  * UI: Use icons from theme on Linux
  * Revert "UI: Add obs.rc to .gitignore"
  * libobs: Fix obs_property_float_set_limits
  * image-source: Re-add fix of repeating images
  * UI: Remove Area downscale filter option
  * UI: Add obs.rc to .gitignore
  * Revert "obs-ffmpeg: Add option to use b-frames as reference"
  * libobs: Fix effect parsing log specifiers
  * rtmp-services: Add GameTips.tv
  * obs-ffmpeg: Use correct calling convention on CreateDXGIFactory1
  * image-source: Add memory usage limit to slideshow
  * libobs/graphics: Add memory usage member to image file
  * libobs: Add function to get libobs object data
  * image-source: Revert slideshow dynamic loading
  * libobs: Fix frame not being cleared
  * CI: Build for Linux on Azure Pipelines
  * CI: Build on Ubuntu Xenial for Travis CI
  * Adjust locales for better consistency
  * libobs-d3d11: Log errors from HasBadNV12Output just in case
  * libobs-d3d11: Improve NV12 validity check for AMD
  * CI: Always send travis webhook and remove IRC sections
  * obs-ffmpeg: Change clear on media end wording for media source
  * cmake: Fix Qt DLL filenames for debug builds
  * UI: Add confirmation dialog for bandwidth test mode
  * UI: Add PAL 25 & 50 FPS as common FPS values
  * UI: Fix yes/no not using localization in no source dialog
  * UI: Change HDD to Disk in locale
  * UI: Add checkbox for Twitch bandwidth test mode
  * CI: Build 32/64 bit Windows parallel on Azure
  * CI: Build for windows on Azure Pipelines
  * obs-text, win-capture: Do not use premultiplied alpha
  * Add "Area" scale filter
  * UI: Fix "What's New" showing again each patch version
  * UI: If from 23.0.1 or 23.0.0, hide activity feed
  * UI: Add Twitch Activity Feed
  * libobs: Remove unnecessary count check
  * libobs: Fix code styling
  * libobs: Fix first frame when output restarted
  * UI: Redo settings icons
  * CI: Fix building on trusty
  * UI: Add (Do not show again) checkbox to dock closing warning
  * Revert "Merge pull request #1418 from cabirdme/qsv_feature_add"
  * Revert "obs-qsv: Enable b-pyramid & change packet priority"
  * UI: Warn when closing dock widgets for first time
  * UI: Add way to exec std::function via invokeMethod
  * obs-ffmpeg: Check avformat context before use
  * obs-ffmpeg: Fix crash on failed audio codec init (for real)
  * UI: Always set first scene collection/profiles
  * obs-ffmpeg: Fix crash on failed audio codec init
  * libobs-d3d11: Check for bad NV12 output on all devices
  * libobs-d3d11: Perform actual test for NV12 driver bug
  * libobs-d3d11: Remove NV12 blacklist
  * libobs: Always query shared texture handle for encoding
  * UI: Add preview/program labels in studio mode
  * decklink: Fix locale (missing word)
  * decklink: Allow selecting input connections.
  * decklink: Fix FC<->LFE channel swap for some devices
  * obs-text: Add text transform property
  * win-dshow: Fix "Highest FPS" algorithm
  * libobs-d3d11: Reset handle and re-lock if texture rebuilt
  * libobs-d3d11: Use discrete function to get shared handle
  * libobs-d3d11: Set acquired bool when texture acquired
  * obs-ffmpeg: Always output SEI
  * obs-ffmpeg: Fix SEI data output
  * frontend-tools: Fix memory leak when reloading scripts
  * UI: Show video container warning when selecting MOV
  * UI: Update tab stop order in Settings
  * libobs: Tell filters that we want to load
  * CI: macOS builds on Azure Pipelines
  * obs-qsv11: Fix crash on destructor after init failure
  * obs-qsv11: Don't try to free non allocated array on destruction
  * cmake: Fix pkg-config handling of libvlc
  * obs-ffmpeg: Fix NVENC blacklisted card check
  * decklink: Update SDK to 10.11.4
  * UI: Add ability to copy & paste filters from the mixer
  * UI: Fix locale for 'disabled' devices in audio settings
  * rtmp-services: Added GamePlank to services
  * image-source: Fix repeating of images with slideshow source
  * libobs-opengl: Log shader compiler errors
  * libobs/media-io: Fix mono upmix
  * UI: Reset replay buffer button on "stop" signal
  * obs-ffmpeg: Add option to use b-frames as reference
  * obs-filters/expander: Various improvements
  * linux-v4l2: Add setting to change color range
  * UI: Automatically generate Windows file description
* Fri Mar  8 2019 jimmy@boombatower.com
- Update to version 23.0.2:
  * UI: Fix "What's New" showing again each patch version
  * libobs: Fix code styling
  * libobs: Fix first frame when output restarted
  * CI: Fix building on trusty
  * UI: Add (Do not show again) checkbox to dock closing warning
  * Revert "Merge pull request #1418 from cabirdme/qsv_feature_add"
  * Revert "obs-qsv: Enable b-pyramid & change packet priority"
  * UI: Warn when closing dock widgets for first time
  * UI: Add way to exec std::function via invokeMethod
  * obs-ffmpeg: Check avformat context before use
  * obs-ffmpeg: Fix crash on failed audio codec init (for real)
  * UI: Always set first scene collection/profiles
  * obs-ffmpeg: Fix crash on failed audio codec init
  * libobs-d3d11: Check for bad NV12 output on all devices
  * libobs-d3d11: Perform actual test for NV12 driver bug
  * libobs-d3d11: Remove NV12 blacklist
  * libobs: Always query shared texture handle for encoding
  * UI: Reset replay buffer button on "stop" signal
  * libobs-d3d11: Reset handle and re-lock if texture rebuilt
  * libobs-d3d11: Use discrete function to get shared handle
  * libobs-d3d11: Set acquired bool when texture acquired
  * obs-ffmpeg: Always output SEI
  * obs-ffmpeg: Fix SEI data output
  * frontend-tools: Fix memory leak when reloading scripts
  * UI: Update tab stop order in Settings
  * CI: macOS builds on Azure Pipelines
  * obs-qsv11: Fix crash on destructor after init failure
  * obs-qsv11: Don't try to free non allocated array on destruction
  * obs-ffmpeg: Fix NVENC blacklisted card check
* Wed Feb 27 2019 jimmy@boombatower.com
- Update to version 23.0.1:
  * obs-browser: Fix widgets being initially blank on high-DPI
  * libobs: Update version to 23.0.1
  * libobs-d3d11: Disable NV12 textures if NVENC unavailable
  * UI: Don't show "What's New" for new users
  * UI: Don't delete auto-remux file (just in case)
  * libobs-d3d11: Blacklist certain adapters from NV12
  * UI: Do not allow post-GPU rescaling on gpu encoders
  * libobs: Add func to get encoder caps by encoder pointer
  * obs-ffmpeg: Fix bitrate being set on NVENC CQP/lossless
  * UI: Fix Mixer allowing endless login retries
  * UI: Make workaround for Logitech plugin hard lock
  * UI: Check CEF available when loading auth
  * libobs-d3d11: Improve check for NV12 texture support
* Tue Feb 26 2019 Jimmy Berry <jimmy@boombatower.com>
- Include pkg-config (.pc) file in devel subpackage.
* Mon Feb 25 2019 jimmy@boombatower.com
- Update to version 23.0.0:
  * UI: Rename a bunch of bad file names
  * image-source: Change max loaded slideshow images to 21
  * enc-amf: Update translations
  * obs-ffmpeg: Add more blacklisted NVENC adapters
  * Update translations from Crowdin
  * UI: Fix replay buffer checked state when no hotkey is set
  * UI: Refine strings for About dialog
  * Update translations from Crowdin
  * UI: Force Twitch moderation tools to system browser
  * UI: Fix wrong filename building for Remux dialog
  * obs-ffmpeg: Free NVENC textures after sending EOS
  * libobs: Update version to 23.0.0
  * obs-browser, obs-vst: Update translations
  * UI: If auth startup failed, keep connected in settings
  * UI: If Twitch account disconnected, retry login
  * UI: If Mixer account disconnected, retry login
  * UI: Fix scene list text edit sizing on dark theme
  * UI: Actually fix non-windows compilation
  * UI: Fix non-windows compilation
  * UI: Do not display threaded message boxes on startup
  * UI: Defer autoconfig to message queue
  * obs-text: Use custom draw flag
  * Update translations from Crowdin
  * UI: Set replay buffer check w/ --startreplaybuffer
  * UI: Fix disabling "resize output to source"
  * UI: Make sure user can still stream if auth fails
  * UI: Do not auto-remux if using FFmpeg output
  * UI: Use QFileInfo for remux
  * UI: Clean up code styling of ternary operator usage
  * UI: Allocate space for null terminator
  * image-source: Actually defer slideshow, not image source
  * obs-frontend-api: Make a few frontend API thread-safe
  * UI: Fix profile duplicates using wrong cookies
  * libobs: Fix missing mutex unlock from 26dbe54
  * libobs: Check fwrite return value for extra safety
  * libobs-d3d11: Fix rebuild of NV12 textures
  * libobs-d3d11: Actually use paired NV12 member variable
  * libobs-d3d11: Don't inline rebuild funcs
  * UI: Fix inconsistent use of ellipsis
  * obs-ffmpeg: Fix constant QP mode in new NVENC
  * UI: Set preferHardware only when hw encoder is avail.
  * UI: Hide instead of disable rescale
  * obs-ffmpeg: Update advice for CFA
  * vlc-video: Fix a video format not playing back correctly
  * UI: Add back auth for custom RTMP servers
  * obs-ffmpeg: Add more blacklisted non-NVENC adapters
  * UI: Disable stream settings if streaming
  * UI: Suggest hw encoding by default depending on hw
  * obs-browser: Update default URL
  * UI: Remove unused help icon
  * frontend-tools: Remove unused help icon
  * UI: Remove unused "Beta" texts
  * obs-browser: Don't use UNUSED_PARAMETER in app class
  * UI: Delete cookies on profile removal
  * obs-ffmpeg: Enable NVENC psycho_aq by default for now
  * obs-browser: Have child processes detect crashes
  * UI: Wait for browser init before "what's new" dialog
  * UI: Clear key in autoconfig when service disconnected
  * UI: Estimate better resolution if using NVENC
  * obs-outputs: Increase GetAdaptersAddresses buffer size
  * decklink-output-ui: Add note about keyer output
  * libobs: Fix indent
  * libobs: Fix race conditions
  * libobs: Fix potential race condition on shutdown
  * UI: Add default preset for NVENC in simple output
  * decklink-ouput-ui: Remove unused help icon
  * frontend-tools: Remove unused help icons
  * UI: Remove additional unused help icons
  * win-capture: Don't try to find window every frame
  * obs-ffmpeg: Mark unused parameter
  * decklink-output-ui: Fix memory leak in save settings
  * obs-ffmpeg: Don't expose new settings to old NVENC (yet)
  * UI: Don't enable rescale if on "Use stream encoder"
  * UI: Fix encoder preset locale text
  * UI: Fix potential race condition for hover items
  * UI: Add OBSBasicPreview::Get helper func
  * obs-ffmpeg: Fix crash when audio not configured
  * UI: Add missing text string for Remux dialog
  * UI: Allow compressed responses in RemoteTextThread
  * image-source: Defer update of slideshow source
  * Revert "UI: Use Twitch dashboard chat popout"
  * UI: Use Twitch dashboard chat popout
  * UI: Remove help icon from auth/what's new titlebars
  * libobs: Fix crash starting raw encoder before gpu encoder
  * UI: Add minimum size of OAuth login dialog
  * UI: Fix autoconfig authentication not working
  * libobs: Fix texture-based encoder decklock
  * UI: Increase Twitch "Stream Stats" height by 50
  * UI: Allow animated BTTV emojis
  * decklink-output-ui: Fix memory leak
  * UI: Enter graphics context before destroying texture
  * libobs: Make sure to destroy effect
  * UI: Make "What's New" dialog modeless
  * obs-ffmpeg: Add a few line breaks for new tooltips
  * UI: Check that CEF loaded before loading integrations
  * obs-ffmpeg: Use CQP in jim-nvenc properties text
  * UI: Fix being unable to drag/drop source list items
  * UI: Fix issue with Mixer
  * UI: Do one time reset of dock lock state for v23
  * obs-ffmpeg: Add tooltips for new NVENC settings
  * UI: Start projector user-facing monitor count at 1
  * UI: Adjust Acri and Rachni themes
  * CI: Build service-integration on Windows
  * image-source: Increase slideshow max loaded to 15
  * obs-ffmpeg: Disable psycho_aq by default (for now)
  * UI: Fix twitch stream stat window not centering
  * UI: Add bttv emote button to Twitch chat window
  * UI: Change preview handles/outline and add hover
  * UI: Add scene item canvas overflow to preview
  * obs-ffmpeg: Do not allow new NVENC on gpu idx > 0
  * enc-amf: Update plugin to Version 2.5.1
  * UI: Use new NVENC by default in simple output mode
  * obs-ffmpeg: Add texture-based NVENC encoder implementation
  * obs-ffmpeg: Update NVENC properties and property defaults
  * obs-ffmpeg: Update display name of FFmpeg NVENC encoder
  * obs-ffmpeg: Update nvEncodeAPI.h to latest version
  * UI: If hardware encoder selected, disable post rescale
  * UI: Use hardware encoding by default if available
  * libobs: Add texture-based encoding support
  * libobs: Split do_encode in to two funcs
  * libobs/media-io: Add frame funcs for separate GPU thread
  * obs-ffmpeg: Implement NVENC video card blacklist
  * libobs/util: Fix bug with get_winver
  * libobs/util: Fix bug with circlebuf_data
  * libobs: Add ability to reroute encoders
  * libobs/util: Add get_win_ver_int() func (windows)
  * libobs: Use NV12 textures when available
  * libobs: Add obs_video_active() function
  * libobs/graphics: Add NV12 texture support
  * libobs/graphics: Add texture sharing functions
  * UI: Fix potential race condition
  * UI: Add Twitch integration
  * UI: Add Mixer integration
  * UI: Add auth. support to settings/autoconfig
  * UI: Add obfuscation func
  * UI: Add Auth and OAuth classes
  * UI: Add func to load browser/cookies, but show dialog
  * UI: Add per-profile browser panel cookie management
  * UI: Switch to new browser panel code
  * UI: Improve/refactor autoconfig/settings service UI
  * UI: Add function for adding extra docks to main window
  * UI: Make assignDockToggle an actual function
  * UI: Add function to get main window more easily
  * UI: Add functions for executing funcs without blocking
  * UI: Add CreateQThread helper function
  * UI: Unlock UI by default
  * UI: Add alternate constructor for RemoteTextThread
  * UI: Add timeout parameter to RemoteTextThread
  * UI: Only def. BROWSER_AVAILABLE for WIN32 (for now)
  * UI: Remove "service type" from auto-config stream page
  * obs-filters: Fix unused parameter warnings
  * obs-vst: Fix resizing on windows (submodule update)
  * UI: Enable high DPI scaling, for Qt >= 5.11
  * UI: Use Next button for GPL license page in windows installer
  * win-capture: Add a few more blacklisted capture exes
  * win-capture: Do not capture "explorer.exe" with null titles
  * libobs: Fix scanf type specifiers
  * frontend-tools: Call modified prop callbacks on script load/reload
  * CI: Use modified macOS QT installer
  * win-capture: Start user-facing monitor count at 1
  * UI: add a default black background to the PGM output of the multiview
  * rtmp-services: Remove LiveEdu from services
  * decklink: Remove redundant const qualifiers
  * UI: Clear out previous projectors when loading saved projectors
  * rtmp-services: Update Twitch and Smashcast ingests
  * obs-filters: Add downward expander filter
  * UI: Fix audio recording for lossless simple (#1616)
  * cmake: Use multiprocessor compilation on Windows (#1605)
  * rtmp-services: restore STAGE TEN (now using rtmps)
  * Use Premultiplied Alpha for Text and Game Capture (#1578)
  * rtmp-services: updating castr.io ingests
  * Add Bangalore, India server to Restream
  * rtmp-services: Add Camplace.com RTMP Services (#1631)
  * UI: Fix a series of mem leaks (#1614)
  * syphon: Remove references to game capture
  * obs-ffmpeg: Show additional details in failed to write error
  * win-capture: Disable cached offsets writing
  * win-capture: Improve reading from get-graphics-offsets
  * obs-qsv: Enable b-pyramid & change packet priority
  * README.rst: Clarify that project is GPL2+
  * Add GPL Cooperation Commitment to base directory
  * UI: Fix accessibility/narration text on sources list
  * UI: Add support for Restream "Auto" server in auto-config
  * decklink: Initialize member variables
  * UI: Fix infinitely incrementing showing ref
  * UI: Set minimum negative sync offset to -950
  * libobs, UI: Do not log redundant warnings
  * UI: Add date/time to log file
  * Authors: Update Contributors list
  * UI: Fix Defaults button not triggering UI update
  * rtmp-services: Update service json format version
  * Decklink: only use RGBA when using keyer
  * obs-qsv11: Log errors on init
  * Decklink: Keyer support
  * libobs: Add get_defaults2 and get_properties2 for encoders
  * rtmp-services: Update Chaturbate POPs
  * libobs: Allow const argument in obs_set_cmdline_args
  * Add Discord badge to README
  * libobs: Fix circlebuf_pop_back returning front
  * libobs: Fix Windows Game Mode detection on newer Windows 10 versions
  * UI: Save scene collection before export
  * UI: Support fractional scaling
  * UI: Revert default tab in Settings > Output: Advanced to Stream tab
  * Add support for building on PPC64LE using x86 Intrinsic Compat Shim
  * libobs: Fix utf-8 bom is not properly skipped
  * UI: Show "OBS Studio" in linux desktop link
  * UI: Fix display of mono source with surround output
  * CONTRIBUTING.rst: Add Discord server and dev chat
  * rtmp-services: Remove dead servers/services
  * linux-v4l2: Make V4L device names unique
  * UI: Add French to UI/dist/obs.desktop
  * win-mf: Initialize member variable
  * rtmp-services: Added Bongacams ingest point
  * UI: Add /LARGEADDRESSAWARE for MSVC x86 executable
  * libobs: Fix crash when pixel or vertex shader are missing
  * libobs: Log audio source when buffering is added
  * libobs: Fix starting timestamp for preloaded frames
  * rtmp-services: Add Restream FTL ingests
  * obs-output: Update ftl-sdk version
  * rtmp-services: Allow seamless service renaming
  * rtmp-services: Add Lightcast.com
  * rtmp-services: Add Linkstream
  * libobs/util: Make default val INVALID_HANDLE_VALUE
  * libobs: Background color of 0 should not be gray
  * CI: Use proper VLC release tarball
  * CI: Use VLC 3.0.4 instead of master for macOS
  * obs-libfdk: Compatibility fix for new API
  * obs-filters: Add limiter filter
  * libobs: memset() the correct buff size
  * libobs: Do not process panning if panning centered
  * decklink: Add declaration file for integer types
  * libobs: Fix audio offset not reset for all tracks
  * CI: Update Qt path on Windows
  * UI: Fix batch remux compiler warning
  * Add AppVeyor CI status badge to README
  * Add Travis CI status badge to README
  * UI: Remove scrollbar line controls for Dark theme
  * Decklink: add UI to control output
  * UI: Fix bug when loading saved projectors
  * UI: Emit STREAMING_STOPPING event immediately
  * linux-capture: XCompCap now chooses glXFBConfigs based on window depth
  * decklink: Initialize member variable
  * UI: Add multi-track FFmpeg output support
  * obs-ffmpeg: Enable multiple audio tracks for FFmpeg output
  * libobs: Add multi-track support to non-encoded outputs
  * UI: Don't transition if already transitioning (studio mode)
  * libobs: Add obs_enum_scenes for enumerating scenes
  * libobs-d3d11: Use mip levels are used in resource view
  * libobs-opengl: Add int2-4 support
  * enc-amf: Update to 2.5.0.1 and update repository address
  * UI: Fix typo with resize output text
  * Revert "Merge pull request #1498 from Xaymar/patch-obs-amd-encoder"
  * Decklink: add output support
  * UI: Fix auto remux warning
  * rtmp-services: Update liveedu.tv servers
  * rtmp-services: Add DLive
  * obs-ffmpeg: Add linux VAAPI h.264 encoding support
  * libobs: Add pkgconfig support
  * enc-amf: Update to 2.5.0 and update repository address
  * UI: Change resize output text
  * linux-capture: Fix repeated swapping of swapRedBlue and improve robustness further
  * rtmp-services: Add Vimm.TV
  * libobs: Truncate thread names on Linux
  * UI: Add ability to resize output based on source size
  * UI: Add option to auto remux
  * UI: Remove '?' from remux title bar
  * CI: Add mbedTLS dependency for AppVeyor Linux
  * CI: Build on Linux with AppVeyor
  * CI: Use cmd prefix on AppVeyor as needed
  * CI: Move AppVeyor install commands to a script file
  * cmake: Find Qt first before going to subdirectories
  * cmake: Fix UI being dependent on browser plugin files
  * UI: Fix array length computation
  * docs/sphinx: Add missing obs_sceneitem_get_id info
  * UI: Fix scrollbar misalignment for Acri theme
  * UI: Fix scrollbar handle alignment for Dark theme
  * libobs: Fix heap corruption in obs_source_output_video
  * image-source: Decrease slideshow source memory usage
  * UI: Fix system tray context menu creation
  * UI: Organize unused/duplicate includes
  * libobs/audio-monitoring: Use libobs CFString utils
  * coreaudio-encoder: Use libobs CFString utils
  * decklink: Use libobs CFString utils
  * mac-capture: Use libobs CFString utils
  * mac-vth264: Use libobs CFString utils
  * libobs: Add CFString utils
  * UI: Undo/fix stats dock changes to main window
  * decklink: Remove inactive audio channels (linux, macOs)
  * UI: Add 4th aux audio input device
  * frontend-tools: Increase instant replay playback retry interval
  * frontend-tools: Add VLC support to instant replay script
  * UI: Batch remux and drag/drop support on remux dialog
  * UI: Change about dialog bottom color (light theme)
  * win-capture: Add option to adjust hook rate for game capture
  * linux-capture: Improve XComposite capture robustness
  * libobs: Don't call width/height funcs if context invalid
  * rtmp-services: Update Lahzenegar settings
  * obs-filters: Add "Invert Polarity" audio filter
  * obs-filters: Avoid skewing chroma key's box filter average
  * obs-filters: Optimize chroma key's box filter
  * cmake: Make static VC runtime libraries consistent
  * Plugins: Add descriptions to modules
  * libobs: Export image-file to c
  * obs-browser: Fix local macOS build issues
  * obs-qsv: enable High Profile for QSV h264
  * UI: Add ability to style preview background color
  * UI: Dark theme padding and alignment fixes
  * UI: Add Filter to Hotkeys settings menu
  * Fix README hyperlinks under Credits
  * cmake: Fix an error when SWIG isn't found
  * UI: Set about dialog as non-resizable
  * docs/sphinx: Add annotation api functions
  * libobs: Add additional gs_effect_get_ functions
  * libobs: Add HLSL annotation parsing
  * Update decklink SDK to version 10.11
  * obs-filters: Add base canvas resolution option
  * libobs/util: Fix undefined behavior and optimize util_mul64_64
  * UI: Add ability to reset sliders when double clicked
  * UI: Implement stereo balancing
  * UI: Remove license agreement dialog
  * UI: Add about dialog
  * cmake: Make directory before copying file
  * decklink: Add deactivate when not showing option to decklink
  * cmake: Add install_obs_data_file function
  * Update AUTHORS file
  * UI: Prevent format-truncation compiler warning
  * obs-outputs: Fix unused variable compiler warning
  * obs-outputs: Make rtmp packet alloc code path clearer
  * UI: Fix not all projectors using ProjectorAlwaysOnTop
  * win-ivcam: Remove and prohibit useless member functions
  * linux-jack: Fix snprintf format specifier
  * libobs: Remove VLA in pulse monitoring backend
  * cmake: Add variable-length array checks
  * libobs: Update version to 22.0.3
  * obs-browser: Fix macOS crash
  * UI: Blacklist LockApp and Text Input from Game Capture
  * UI: Add retina support and updated icons
  * UI: Add rename scene/source shortcut
  * libobs-opengl: Store FBOs per texture instead of per device
  * UI/updater: Fix update bug for 32bit/64bit installs
  * UI: Add ctrl+up/down shorcuts to move filters around
  * UI: Add delete as shortcut for removing filters
  * UI: Make stats dockable
  * rtmp-services: Remove offline/unavailable servers/services
  * rtmp-services: add STAGE TEN
  * UI: Name parameters in definition same as in declaration
  * image-source: Add psd and *.* to file filter
  * UI: Use themeID for red message in settings view
  * obs-qsv: Expose additional QSV encoder settings through GUI
  * libobs/UI: Allow Access To argc/argv
  * win-capture: Modify log for sharedmem
  * obs-filters: Use less automagic for SpeexDSP detection
  * deps/obs-scripting: Use less automagic for Lua/Python detection
* Fri Dec  7 2018 Jimmy Berry <jimmy@boombatower.com>
- Remove workaround for utilizing proper libdir as it interferes
  with building plugins.
* Wed Nov 14 2018 Jimmy Berry <jimmy@boombatower.com>
- Set ExclusiveArch to i586 and x86_64.
* Wed Nov 14 2018 Jimmy Berry <jimmy@boombatower.com>
- Restrict to ffmpeg3 to avoid Tumbleweed segfault.
  https://bugs.links2linux.org/browse/PM-143
* Thu Sep 13 2018 jimmy@boombatower.com
- Include optional build dependencies to enable more features.
* Fri Aug 31 2018 jimmy@boombatower.com
- Update to version 22.0.2:
  * Revert "UI: Do not fire load events until program loaded"
  * Revert "UI: Reset sources list manually on first load"
  * UI: Always show filter preview if video source
  * obs-browser: Update version to 2.1.5
  * UI: Reset sources list manually on first load
  * UI: Remove "Beta" from auto-config tools menu text
  * libobs: Update version to 22.0.2
  * obs-browser: Update version to 2.1.4
  * UI: Make sure quick transition hotkey is not zeroed
  * UI: Do not fire load events until program loaded
  * UI: Use AlwaysOnTop option for windowed projectors
  * UI: Fix a rare multiview crash when clicked
  * UI: Fix macOS bug (scrollbar blocking lock icons)
  * CI: Use Qt 5.10.1 instead of 5.11.1 for macOS
  * UI: Remove beta warning from auto-config wizard
  * libobs: Blacklist old obs-browser version on macOS
  * UI: Fix filter layout issue
  * UI/updater: Add missing header
  * obs-outputs: Revert f1f49bc1 to fix RTMP authentication
  * UI: Select item that user adds
  * CI: Rename one more missed cef-bootstrap name
  * CI: Rename cef-bootstrap to obs-browser-page
  * obs-browser: Update browser version to 2.1.3
  * UI: Set browser hwaccel def. to false if winver <=7
  * rtmp-services: Only do URL check for Facebook
  * UI: Close remux output before showing dialog
  * rtmp-services: update Periscope settings
  * CI: Use env variable for CEF cache on Windows
  * CI: Build Browser Source on Windows
  * UI: Use QT font picker on OSX
* Tue Aug 21 2018 jimmy@boombatower.com
- Update to version 22.0.1:
  * obs-browser: Update translations
  * libobs: Update version to 22.0.1
  * obs-browser: Fix local files not being processed correctly
  * libobs: Update to version 22.0.0
  * UI: Fix path for File > Show Recordings
  * obs-browser: Blacklist certain hwaccel adapter combos
  * UI: Fix mixer context menu toggling layout on kde
  * cmake: Add luajit 2.1 support to build
  * obs-browser: Update version number to 2.1.0
  * libobs: Revert version update to 22.0.0 (instead, do RC2)
  * UI: Fix snapping of group sub-items
  * CI: Use HTTPS for downloading macOS deps package
  * libobs: Fix typo in function names
  * UI: Remove warning when using separate QSV encoders
  * Update translations from Crowdin
  * Update translations from Crowdin
  * updater: Prepare for transition to Fastly CDN
  * libobs: Update version to 22.0.0
  * UI: Hide Dock Icon on Mac OSX when minimizing to tray
  * UI: Update Acri theme
  * UI: Fix multiview hang
  * Revert "UI: Use qss themeID for red labels in properties view"
  * UI: Fix dark theme link color
  * UI: Update Rachni theme
  * obs-browser: Fix "shutdown when invisible" issue
  * UI: Use qss themeID for red labels in properties view
  * UI: Use theme for red message in audio settings
  * UI: Allow centering/stretching for groups items
  * UI: Fix group sub-item selection bug
  * UI: Fix flip/rotate transform menu with group items
  * libobs: Add function to force a sceneitem transform update
  * UI: Fix bug grabbing handles of group sub-items
  * rtmp-services: Add DTube
  * UI: Set replay buffer button as checkable
  * libobs: Fix applying group transform of flipped sources
  * UI: Allow resetting transform of group sub-items
  * rtmp-services: Do not check for valid URL if using "auto"
  * libobs: Initialize hotkey pair ID variable properly
  * UI: Allow the transform dialog for group sub-sources
  * UI: If users renames a source, only revert on Esc
  * obs-browser: Fix a number of bugs
  * UI: Protect GUID generation in mutex
  * UI: Make the information dialog a big wider
  * UI: Add release candidate checking to info dialog
  * cmake: Add release candidate versions/cmake variables
  * libobs/media-io: Prevent overwriting of remux input
  * libobs: Update version from latest tag
  * obs-qsv11: Protect context variable in clear_data
  * rtmp-services: Remove unnecessary null check
  * libobs: Remove unnecessary null check
  * UI: Add adv. settings checkbox for browser HW accel
  * libobs: Add functions to get/set global private data
  * libobs: Move function declarations to correct spot
  * UI: Use NVIDIA laptop GPU hint
  * CI: Update OSX Deps package
  * win-capture: Avoid segfault when retrieve size
  * cmake: Prevent policy CMP0072 warning
  * Revert "libobs-d3d11: Initialize variable to zero"
  * win-capture: Avoid tex size mismatch for cursor
  * UI: Make OBS bitness more specific in title bar and log
  * obs-qsv11: Initialize member variable
  * CI: Fix building libvpx dep on osx
  * rtmp-services: Ensure set URL exists within server list
  * rtmp-services: Change Facebook stream URL to use RTMPS
  * obs-outputs: Add support for and use mbedTLS for SSL
  * libobs: When ungrouping groups, duplicate items
  * libobs: Add internal function to dup. scene item data
  * libobs: Add function to save hotkey pair data
  * UI: Remove QNetworkReply from window-basic-main.hpp
  * UI: Use obsproject.com URL for discord invite
  * libobs-opengl: Fix segfault on access of invalid window
  * libobs-opengl: Improve X error handler message
  * obs-filters: Fix segfault in Compressor Filter
  * UI: Add missing va_end() call
  * CI: Update macOS dependencies in build script
  * CI: Update Travis scripts to target OSX 10.11+
  * CI: Update Travis Mac builds to Xcode 9.4 and macOS 10.13
  * UI: Add ability to join discord server from help menu
  * UI: Add Color Coding to Source Tree Widget
  * win-mf: Add missing va_end() call
  * obs-browser: Add hardware acceleration option (win32)
  * UI: Add missing return statement
  * UI: Uncheck record/replay buffer buttons if fail
  * UI: Use QScopedPointer (not QPointer) where applicable
  * UI: Hide preview for sources and filters where possible
  * UI: Fix disabled items in Dark theme being too light
  * libobs: Log libobs bitness in crash logs
  * UI: Add confirmation dialog if there are no sources
  * libobs-d3d11: Initialize variable to zero
  * UI: Check pointer before the first dereference
  * UI: Add intro startup page (windows)
  * deps: Add json11 library for convenience
  * UI: Only allow stream/record hotkeys if the UI buttons are enabled
  * OSX: Add NSCamera and NSMicrophone UsageDescription for 10.14
  * CI: Use Qt 5.11.1 on Travis for macOS
  * CI: Use Qt 5.11.1 on AppVeyor for Windows
  * frontend-tools: Add QAction explicitly for Qt 5.11 compatibility
  * Fix typo in contributor guide
  * UI: Fix start up crash with saved projectors
  * rtmp-services: Add Piczel.TV server
  * enc-amf:  Version 2.4.2
  * libobs: Always try to update transform in current thread
  * libobs: Only update scene item texture on frame tick
  * libobs: Don't assign variables before if/return
  * UI: Do not open properties dialog for groups
  * obs-outputs: Update librtmp with upstream patches
  * CI: Add AppVeyor webhook for Discord bot
  * CI: Add travis webhook for Discord bot
  * UI: Add signal for when theme has changed
  * UI: Add ability to parse OBSStyle from qss
  * libobs: Copy the device uid string for mac audio monitor
  * libobs: Pass address of cf_uid rather than the contents of cf_uid
  * libobs: Fix setting of audio monitor device on Mac
  * libobs: Rework checking Mac audio device capabilities
  * UI: Fix bug with advanced output service settings
  * libobs: Add function to get encoder object's defaults
  * obs-browser: Fix error and warning
  * obs-browser: Update to latest version
  * libobs: Defer update of scene item texture
  * UI: Allow alt-cropping on bounding box scene items
  * libobs/util: Don't use assert for darray_push_back_array
  * obs-qsv:  Allow for multiple QSV encoders
  * obs-output: Update ftl-sdk version
  * CI: Update Sparkle default base_url
  * rtmp-services: Update ingest list for Restream.io
  * rtmp-services: Update ingest list for GamePlank
  * UI: Fix signals for sub-items of groups
  * UI: Add OBSBasic::SavingDisabled() function
  * UI: Allow copying/pasting of groups
  * libobs: Allow group duplication
  * libobs: Change groups to actual public types
  * libobs: Abstract resize_group to resize_scene_base
  * libobs: Refactor creation of scenes
  * libobs: Remove group_sceneitem from obs_scene struct
  * libobs: Add obs_data_array_push_back_array
  * Update INSTALL
  * UI: Fix OBS_FRONTEND_EVENT_TRANSITION_LIST_CHANGED
  * rtmp-services: Add KakaoTV
  * libobs: Update libcaption library
  * rtmp-services: Adding Castr.io ingests to service list
  * vlc-video: Load libvlccore.dylib on macOS
  * CI: Fix CEF Path on Package Build
  * libobs: Remove unnecessary const qualifier
  * libobs: Remove unused variable
  * libobs: Remove unused variable
  * libobs: Fix equality check
  * libobs: Add missing return type
  * libobs: Remove unused variable
  * libobs: Change int to size_t
  * UI: Fix stream button checkable state
  * UI: Update Acri theme for disabled buttons
  * UI: Add frontend event for when OBS finishes loading
  * Revert "obs-x264: Specify x264 color space for BT.601"
  * UI: Fix cramped source tree sub-widgets on macOS
  * UI: Fix bug where color property shows transparency
  * UI: Fix display bug with color property
  * libobs: prevent crash from unbounded copy and bfree
  * UI: If group's name exist, start it from 2
  * UI: Fix mixer dock widget minSize being too big
  * obs-transitions: Fix potential stinger divide by 0
  * libobs: add obs_source_frame_copy
  * libobs: Fix compilation issue on case-sensitive filesystems
  * libobs: Add check for cf_uid pointer free
  * libobs: Fix Monitoring devices showing input devices
  * obs-x264: Specify x264 color space for BT.601
  * UI: Fix mem leak in VolControl
  * librtmp: Fix memory leak
  * UI: Fix mem leak with QCompleter
  * UI: Fix mem leak with multiview projector menu
  * UI: Fix mem leak with tray menu
  * UI: Fix mem leak with volume meter
  * UI: Compact ClearVolumeControls()
  * UI: Update hotkey label on quick transition rename
  * libobs: Update hotkey label on scene item rename
  * libobs: Enable setting hotkey name and description
  * UI: Add grouping
  * UI: Fix missing newline at the end of a file
  * UI: Refactor DrawCircleAtPos
  * UI: Use vector value for nudge callback
  * UI: Move frontend API initialization to constructor
  * libobs: Add scene item grouping
  * libobs: Add custom size support to scenes
  * libobs: Do not signal reorder while scene mutex locked
  * libobs: Defer and refactor scene item transform update
  * libobs: Refactor item signaling (add func to signal parent)
  * libobs: Do not draw item texture if source size 0
  * libobs: Fix bug where cropped items would recalc transform
  * libobs: Zero scene data instead of setting members manually
  * libobs/callback: Add signal reference counting
  * libobs: Refactor obs_scene_add to allow adding internally
  * UI: Fix a few unused lambda closure captures
  * libobs: Copy metadata for tracks/streams when remuxing
  * obs-filters: Use double-precision where viable
  * libobs: Avoid busy cursor when starting processes
  * libobs: Allow custom core data paths
  * libobs: Handle 'in', 'out', and 'inout' keywords in shader parsers
  * obs-ffmpeg: Set average framerate in video stream
  * Make alpha visible in property color
  * Use selected color in color property label
  * CI: Upgrade to VS2017 on Appveyor
  * UI: Add new Multiview Layout for up to 24 scenes
  * UI: Move more fixed values to multiview update
  * UI: Adjust the multiview num sources by the layout
  * UI: Calculate fixed values of the Multiview once
  * UI: Move multiview setting checks from draw path
  * UI: Add option to toggle multiview draw safe area
  * UI: Update multiview safe areas
  * UI: Add option to toggle multiview scene names
  * UI: Add option to toggle multiview mouse switching
  * UI: Move multiview settings to its own groupbox
  * UI: Update multiview on scene list reorder
  * UI: Update multiview on resolution change
  * UI: Adjust multiview label size
  * UI: Add proper source markers to multiview
  * UI: Simplify multiview draw code
  * UI: Change multiview non-studio selection color
  * UI: Remove the outerbox markers in multiview
  * UI: Make the multiview lines use the same color
  * UI: Make the sources border color a little darker
  * UI: Clean up Projector Creation
  * UI: Clean up projector's render regions creation
  * UI: Make multiview colors easier to manage
  * UI: Clarify multiview layout names
  * UI: Convert multiview layout string profiles to int
  * UI: Use enum for multiview layout
  * UI: Add Vertical Mixer option
  * UI: Simplify Volume Control draw logic
  * UI: Avoid copies in Volume Control
  * UI: Clean up includes and code-style
  * CI: Use QT 5.10.1 for AppVeyor builds
  * Use obsproject.com for log file uploads
  * UI: Fix OBS_FRONTEND_EVENT_PREVIEW_SCENE_CHANGED
  * UI: Remove ENABLE_WIN_UPDATE cmake variable
  * UI: Always enable auto-updater for windows
  * UI: Fix memory leak when drag/dropping
  * text-freetype2: Remove trailing whitespace
  * text-freetype2: Add chat line count property
  * libobs: Use xcb-xinput when available for events
  * cmake: Add xcb-xinput support
  * UI: Add opt. to enable/disable in-focus hotkey blocking
  * win-capture: Fix cursor draw size with certain cursors
  * win-dshow: Allow synchronous create/update
  * UI: Block when calling obs_frontend_set_current_scene
  * UI: Add obs_frontend_add_scene_collection API call
  * UI: Use WaitConnection() when adding scenes
  * UI: Add WaitConnection() helper func
  * UI: Use "source_create" to add scenes to listbox
  * libobs: Make callback optional for obs_load_sources
  * libobs: Don't signal "source_create" for private sources
  * win-capture: Update D3D9 signature for Win10 April 2018 Update
  * libobs: Expose source save/load signal
  * docs/sphinx: Fix typo in script sources section
  * obs-browser: Use BGRA textures instead of RGBA
  * UI: Don't defer load on non-macOS systems
  * UI: Also defer first scene collection load
  * libobs: Use unaligned store rather than aligned store
  * libobs: Convert sse inline funcs to macros
  * libobs: Add "static" to inline func
  * libobs, UI: Add true peak measurements
  * rtmp-services: Update ingest list for Restream.io
  * UI: Fix no_space file naming for replays
  * UI: Explicitly initialize the crash handler
  * libobs: Separate crash handler from startup
  * UI: Change remux dialog to be non-modal
  * libobs: Add functions to get output capability flags
  * win-capture: Avoid obs functions in init_hooks
  * libobs: Add functions to get raw video output
  * libobs: Deactivate unnecessary GPU ops when not encoding
  * libobs: Log *nix window manager
  * UI: Disable paste filters unless a source is selected
  * CI: Add description to OSX deps build script
  * .gitmodules: Update submodules to new obsproject org
  * UI: Set OBS icon to projector and stats window
  * libobs-d3d11: Do not allow Alt+Enter interception
  * UI: Sort audio controls by source name
  * libobs: Add function to get last main output texture
  * libobs: Fix potential filter rendering race condition
  * UI: Clean up delete Source/Scene shortcut
  * UI: Don't close windows for "Always on Top" (win32)
  * UI: Hold the clip flash for at least one second
  * UI: Add Selected and Hidden Array Values
  * UI: Move OpenSavedProjecters call to OBSBasic::Load()
  * obs-ffmpeg: fill in more fields on audio frames
  * libobs: Fix pasting filters crash when missing sources
  * UI: Do not generate "already active" logs
  * obs-browser: Update to browser source refactor
  * CI: Reduce travis output verbosity
  * UI: Defer startup OBSBasic::Load (macOS CEF workaround)
  * UI: Change monitoring device on profile change
  * UI: Add frontend API to defer saving
  * rtmp-services: Update recommended parameters for Nood.tv
  * obs-outputs/flv: Fix ECMA array size
  * CI: change travis osx artifact repo name
  * UI: Save windowed projectors on exit
  * UI: Remove a second call to OpenSavedProjectors
  * UI: Clean up OBSProjector creation
  * UI: Update Projectors title on source name change
  * UI: Clean up save and load projector code
  * UI: Add helper functions to Projector
  * UI: Add Scene to ProjectorType
  * UI: Simplify Projector Init
  * UI: Refactor Projector OBSRender source usage
  * UI: Move ProjectorType enum to projector header
  * UI: Make OpenSavedProjectors indentation clear
  * UI: Fix the Multiview window not using translation
  * UI: Check if source is valid earlier
  * UI: Simplify the OpenProjector logic
  * UI: Only load projectors if SaveProjectors is true
  * frontend-tools: Include 'QAction' to fix build against Qt 5.11
  * mac-vth264: Fix video info set logic
  * mac-vth264: Set the fullrange variable before calling vt_h264_video_info
* Sat May 12 2018 jimmy@boombatower.com
- Update to version 21.1.2:
  * libobs: Update version to 21.1.2
  * win-capture: Update D3D9 signature for Win10 April 2018 Update
  * CI: Check out OSX branch of obs-browser
  * cmake: Include windows style DLL when copying Qt files
  * obs-browser: Update submodule to latest version
  * UI/updater: Delete visual studio runtimes after execution
  * deps/obs-scripting: Prevent python unload more than once
  * obs-browser: Update submodule to latest version
  * deps/obs-scripting: Don't allow unloading more than once
  * enc-amf: Version 2.3.3
  * libobs: Update version to 21.1.0
  * deps/obs-scripting: Add obs_source_enum_filters
  * rtmp-services: Update ingest list for Aparat.com
  * mac-capture: Fix bug where audio device couldn't be changed
  * UI: Add Help -> Crash Reports submenu
  * UI: Add subdir param to OBSBasic::UploadLog
  * UI: Specify whether crash/profiler/logs have prefix
  * UI: Specify subdir/variable to save to for get_last_log
  * rtmp-services: Update ingest list for Nood.tv
  * UI: Replace gist with hastebin for log uploads
  * UI/updater: Return false on integrity check failure
  * UI/updater: Don't update modules of opposite arch
  * UI/updater: Add automatic check/install for VS2017 redist
  * UI/updater: Fix a few type size mismatch warnings
  * UI/updater: Fix resource compiling bug
  * UI/updater: Fix bug with restrict keyword on VS2017
  * UI/updater: Set license of windows update module to ISC
  * UI/updater: Rewrite function
  * Update translations from Crowdin
  * UI: Refresh multiview projector menu per click
  * cmake: Remove extraneous checks
  * UI: Refresh system tray projector menu per click
  * UI: Remove unnecessary casts
  * Update README.rst
  * libobs-opengl: Request at least 8 bits for alpha
  * linux-capture: Request at least 8 bits for alpha
  * UI: Remove check for updates on Linux
  * cmake, libobs, win-capture: Fix VS2017 warnings
  * cmake: Add .vs directories to .gitignore
  * deps/obs-scripting: Fix tick function arg number
  * obs-ffmpeg: Fix locale typo
  * rtmp-services: Update ingest list for Restream.io
  * deps/obs-scripting: Expose obs video info to swig
  * image-source: Fade to transparency if slideshow list is cleared
  * rtmp-services: Add Vimeo to services list
  * libobs: Fix property text typo
  * libobs/util: Fix blank config file values being ignored
  * obs-ffmpeg: Use FFmpeg's "fast" AAC encoder by default
  * obs-ffmpeg: Remove cutoff hack for AAC encoder
  * win-mf: Deprecate plugin
  * win-capture/graphics-hook: Fix memory offset calculation
  * UI: Remove duplicate line
  * obs-output: Update ftl-sdk version and ftl logging values
  * enc-amf: Version 2.3.2
  * UI: Allow nested docks
  * UI: Don't draw bounding boxes for sources without video flag
* Wed Feb 21 2018 jimmy@boombatower.com
- Update to version 21.0.3:
  * libobs: Update to version 21.0.3 (mac update)
  * libobs: Log YUV space/range on video reset
  * obs-filters: Clear unused parameter warning
  * libobs/util: Cache windows CPU frequency
  * rtmp-services: Add SermonAudio to services list
  * libobs-opengl: Log adapter and driver info
  * obs-ffmpeg: Add speed percentage option
  * deps/media-playback: Use a struct for media init data
  * UI: Remove __FUNCTION__ usage
  * UI: Import scene collection with correct filename
  * obs-vst: Add layout to QMacCocoaViewContainer (update submodule)
  * UI: Link Qt5::MacExtras
  * obs-vst: Link Qt5::MacExtras (update submodule)
  * libobs/media-io: Change speaker layout to match FFmpeg aac.
  * CI: Include style plugins when packaging on OSX
  * CI: Comment out OSX _obspython copy (not ready yet)
  * deps/obs-scripting: Fix cur. script being NULL for script_tick
  * deps/obs-scripting: Allow NULL script with script_log
  * UI: Fix grayed out Copy option in sources context menu
  * CI: Don't install python for OSX
  * cmake: Fix LuaJIT search
  * CI: Add rpath info to _obspython
  * CI: Move obspython.so so it can be found in a .app
  * CI: Update python rpath on osx
  * CI: Make sure that lua can find obslua
  * CI: Fetch RVM gpg key on osx
  * CI: Fix a ruby issue on travis OSX
  * CI: Update OSX deps build scripts
* Thu Jan 25 2018 jimmy@boombatower.com
- Update to version 21.0.2:
  * libobs: Update version to 21.0.2 (mac tag)
  * CI: Point to newer brew python
  * deps/obs-scripting: Make ENABLE_SCRIPTING a user variable
* Tue Jan 23 2018 jimmy@boombatower.com
- Update to version 21.0.1:
  * obs-filters: Fix hard cross-lock when using ducking
  * win-dshow: Fix decoding issues from encoded devices
  * UI: Acri theme adjustments
  * libobs: Update version to 21.0.1
  * docs/sphinx: Clarify Python windows installation
  * CI: Install swig and luajit for osx travis
  * deps/obs-scripting: Prevent potential python startup issues
  * enc-amf: Prevent detect-amf from showing fail dialogs
  * UI: Reduce size of "refresh" icons
  * Revert "obs-outputs: Fix FMS auth with query string"
  * UI: fix Multiview labels readability
  * Update translations from Crowdin
  * CI: Enable scripting in Linux builds
  * cmake: Search for Python 3.4
  * CI: Update CEF version on travis for osx
  * libobs: Update version to 21.0.0
  * UI: Add simple output mode encoder fallback
  * frontend-plugins: Only show script file names in script dialog
  * enc-amf: Test for AMF support in separate process first
  * obs-ffmpeg: Remove NVENC detection code for now
  * UI: Add command line arguments to log
  * obs-ffmpeg: Fix signed mismatch warning
  * frontend-tools: Fix a few issues with the clock source script
  * frontend-tools: Add script to update text source from URL
  * deps/obs-scripting: Fix script_log in python to append newline
  * frontend-tools: Add a lua script that draws an analog clock
  * UI: Add audio meter decay rate option
  * UI: Optimize theme PNG images (smaller files)
  * frontend-tools: Add "Clear" button to script log window
  * frontend-tools: Warn if no active replay buffer w/ instant replay
  * frontend-tools: Make instant replay script also save replay
  * frontend-tools: Add "instant replay" script
  * obs-ffmpeg: Do not return last replay path if currently muxing
  * libobs/callback: Add calldata_create and calldata_destroy
  * deps/obs-scripting: Fix frontend API lua table creation
  * deps/obs-scripting: Fix a few more VC warnings from swigluarun.h
  * obs-ffmpeg: Add proc to get last replay buffer
  * deps/obs-scripting: Ensure that ffi module gets loaded
  * UI: Add Acri theme
  * obs-ffmpeg: Call av_register_all before nvenc check
  * obs-ffmpeg: Don't try to detect NVENC on mac
  * obs-ffmpeg: Improve NVENC detection
  * linux-pulseaudio: Surround speaker map
  * UI: Set max size for names in name dlg. to 256
  * UI: Use snprintf and std::string when creating profiles
  * libobs: Fix rendering if filter context no longer exists
  * libobs: Fix double -> float conversion warning
  * libobs: Optimize clearing of unused source audio mixes
  * libobs: Fix audio buffer clear in custom source mixing
  * Fix typo in README.rst
  * deps/obs-scripting: Fix installed files/locations on linux
  * UI: Put clip detection back in to volume meter
  * deps/obs-scripting: Add image-file to lua
  * deps/obs-scripting: Set current_lua_script earlier to prevent a crash
  * UI: Set linker flags required for luajit on OSX
  * deps/obs-scripting: Don't crash obs trying to unload a script that failed to load
  * docs/sphinx: Clarify vertex buffer usage
  * test/test-input: Add audio buffering sync test source
  * win-capture: Make minor clarification to locale string
  * UI: Fix tab bars for docked widgets in Dark theme
  * libobs: Fix log message
  * Revert "obs-ffmpeg: Improve NVENC detection"
  * deps/media-playback: Free frame data before freeing frame
  * deps/media-playback: Use avcodec_free_context when possible
  * CMake: Fix FindSwigDeps search path
  * UI: Disable Youtube bandwidth test (for now)
  * UI: Fix warning
  * UI: Use GDI+ text for multiview on windows
  * libobs-d3d11: Allow multiple display captures of same monitor
  * UI: Fix qpushbutton menu icon
  * UI: Style dock widgets in dark and rachni themes
  * libobs: Fix audio issue with scene items
  * UI: Add the "-60" volume control marker
  * decklink: Default to 5.1 if invalid channel value 7
  * decklink: Fix bug with old channel formats
  * UI: Change default theme to dark for new users
  * win-capture: Change string for memory capture option
  * linux-pulseaudio: Default sample format float32le
  * cmake: add more LuaJIT lib names
  * Revert "CI: Add Python path for AppVeyor"
  * frontend-plugins: Add "Description" string
  * frontend-plugins: Remove unused strings
  * cmake: Fix copying lua51.dll (luajit) dep on windows
  * CI: Add Python path for AppVeyor
  * deps/obs-scripting: Fix swig/python lookup on windows
  * libobs: Fix pulseaudio monitor playback stuttering
  * libobs: Fix for int-in-bool-context-warning
  * rtmp-services: Add Twitch Helsinki ingest
  * obs-outputs: Fix FMS auth with query string
  * UI: Add frontend API funcs for enabling/disable preview
  * mac-capture: Update fix for Soundflower
  * decklink: Add 2.1 & 4.1 surround layouts
  * coreaudio-encoder: Surround sound improvements
  * obs-libdk: Unlock bitrates for surround layouts
  * UI: Add Multiview Layout Options
  * UI: Add Single/Double click options to Multiview
  * UI: Add help portal link to help menu
  * libobs/media-io: Replace quad with 4.0
  * libobs/media-io: Clean surround API
  * UI: Rework volume-meters, adding more information
  * obs-filters: Fix heavy distortion in Noise Suppression filter
  * libobs: Fix scene filter duplication
  * libobs: Fix bad source release placement
  * obs-filters: Fix minor leaks with LUT filter
  * UI: Fix possible source reference leakage
  * docs/sphinx: Fix vec3_set
  * libobs: Log which security software is in use
  * deps/scripting: Add python rpaths to the obs binary on OSX
  * docs/sphinx: Add scripting documentation
  * doc/sphinx: Add frontend API documentation
  * frontend-tools: Add scripting tool
  * deps/obs-scripting: Add scripting support
  * libobs: Add obs_property_set_modified_callback2
  * libobs: Add obs_properties_add_button2
  * libobs: Fix function to be static inline
  * libobs: Exclude certain declarations from SWIG processing
  * UI: Allow temporarily disabling filter/source types
  * UI: Do not show deprecated filters
  * UI: Add scene collection cleanup event to frontend API
  * UI/obs-frontend-api: Move function declarations
  * UI: Trigger scene change event on scene collection load
  * UI: Add refresh/reload button icons
  * UI: Call frontend callbacks in reverse order
  * UI: Add preload callbacks to frontend API
  * UI: Set ENABLE_UI and DISABLE_UI as root CMake variables
  * libobs: Prevent access to OBS context during shutdown
  * libobs: Store string copies in properties
  * libobs: Add ability to disable source types
  * libobs/callback: Add global callback to signal handler
  * libobs/callback: Add signal_handler_remove_current func
  * libobs/util: Add THREAD_LOCAL macro
  * libobs: Add video tick callback functions
  * cmake: Add helper module for finding Lua
  * cmake: Add Lua/Luajit as part of MSVC dependencies
  * libobs/util: Ignore PRINTFATTR if using SWIG preprocessor
  * libobs/util: Optimize strlist_* functions
  * libobs: Add obs_source_info::get_properties2
  * libobs: Add obs_source_info::get_defaults2
  * linux-v4l2: Add 4k and 21:9 resolutions
  * libobs: Add obs_render_main_texture
  * libobs: Fix incomplete struct in scaler call
  * UI: Fix minor Rachni theme bugs
  * obs-ffmpeg: Fix ffmpeg output recording in x264
  * libobs: Make get_reg_dword handle missing keys
  * Fix typo in README
  * Move documentation to links in CONTRIBUTING file
  * Add documentation links
  * win-capture: Fix memory capture crash on new capture
  * enc-amf: Version 2.3.1
  * win-capture: Rename structs to avoid SDK conflict
  * rtmp-services: Add Twitch Salt Lake City ingest
  * ui: Fix unsaved changes dialog showing twice
  * Fix a number of GCC warnings
  * Fix a number of MSVC warnings
  * obs-ffmpeg: Use correct function with older FFmpeg vers.
  * libobs/media-io: Add ifdef for newer FFmpeg functions
  * Fix a number of MSVC warnings
  * obs-vst: Fix a few warnings (update submodule)
  * cmake: Correct CMake checks for LINUX
  * Revert "CI: Linux - Install FFmpeg from source"
  * git: Add Clion to .gitignore
  * cmake: Do not require X11 on OSX
  * CI: Fix Mac builds on Travis CI's Xcode 8.3 image
  * UI: Duplicate when double-click switching is used
  * UI: Move multiview options to view menu
  * UI: Fix draw issues with multiview projector
  * obs-filters: Add sidechain source option to compressor
  * libobs/util: Add funcs to push zeroed data to circlebufs
  * decklink: Rename 5.1 and 7.1 multi-channel formats
  * rtmp-services: Remove Coderwall / Fix Livestream service name
  * deps/media-playback: Fix compilation with older FFmpeg versions
  * obs-ffmpeg: Improve NVENC detection
  * rtmp-services: Add Mobcrush to services list
  * CI: Fix macOS builds on Travis CI's Xcode 8.3 image
  * UI: Add Multiview projector
  * libobs/graphics: Add gs_effect_set_color
  * CI: Fix Mac builds on Travis CI's Xcode 8.3 image
  * UI: Fix issue where studio preview scene would stick
  * UI: Fix scene override when switching off studio mode
  * UI: Don't override transition if quick transition
  * UI: Fix preview/program projectors being swapped
  * UI: Implement per-scene transition overriding
  * libobs: Duplicate private scene/source settings
  * UI: Fix studio program projectors
  * CI: fix curl download if file doesn't exist
  * win-dshow: Improve automatic Elgato audio device selection
  * UI: Add Studio Mode layout option for portrait mode displays
  * UI: Fix bug with studio mode double-click switching
  * libobs: Fix height return value condition
  * docs/sphinx: Add sphinx documentation
  * libobs: Add vertex/index buffer "direct" flush functions
  * libobs: Add option to duplicate vertex/index buffer data
  * libobs-opengl: Make update_buffer data param const
  * UI: Add Studio Preview Projector
  * UI: Add transition on double-click studio mode option
  * linux-capture: Log window capture's target
  * mac-capture: Log window capture's target
  * win-capture: Log window capture's target
  * libobs: Add surround sound audio support
  * cmake: Add CMake option to disable building plugins
  * UI: Fix a memory leak when renaming mixer sources
  * rtmp-services: Add MyLive streaming platform
  * CI: Update curl version used by appveyor
  * rtmp-services: Add Lahzenegar.com streaming platform
  * libobs-d3d11: Fix gs_enable_color
  * UI: Add ability to rename audio sources from the mixer
  * win-wasapi: Fix timestamp calculation
  * obs-ffmpeg: Log bad muxer settings with FFmpeg output
  * obs-ffmpeg: Use muxer settings with AVIOContext
  * obs-vst: Update to latest plugin version
  * UI: Make streaming/recording buttons checkable
  * UI: Handle update_properties signal in OBSBasicFilters window
  * libobs: Copy enabled state when duplicating filters
  * UI: Allow keyboard events on X11 fullscreen projector
  * rtmp-services: Add Eventials streaming platform
  * rtmp-services: Add us-west1 Picarto ingress
  * UI: Add Frontend API function to save replay buffer
  * UI: Disable source copy if no sources are selected
  * linux-alsa: Display the "Custom" entry once only
* Fri Nov 17 2017 jimmy@boombatower.com
- Update to version 20.1.3:
  * libobs: Update to version 20.1.3
  * libobs: Fix FFmpeg constants
  * libobs: Update to version 20.1.2
  * libobs-d3d11: Allow rebuild even if output duplicator fails
  * graphics-hook: blacklist OpenGL capture for "cm_client.exe"
  * UI: Fix custom ffmpeg output file / URL entry
  * linux-pulseaudio: Get correct default device
  * libobs: Rename obs_video_thread to obs_graphics_thread
  * libobs: Use new ffmpeg constants
  * obs-ffmpeg: Use new ffmpeg constants
  * deps/media-playback: Use new ffmpeg constants
  * UI: Log when output timer events stop outputs
* Thu Oct 26 2017 jimmy@boombatower.com
- Update to version 20.1.1:
  * libobs: Add wrapper function to query Windows registry
  * libobs: Log Windows 10 Gaming Features
  * CI: Update Travis script to target OSX 10.10+
  * enc-amf: Version 2.2.4
  * libobs: Update to version 20.1.1
  * rtmp-services: Add Picarto eu-west1 ingress server
  * rtmp-services: Add stream.me streaming platform
* Wed Oct 18 2017 jimmy@boombatower.com
- Update to version 20.1.0:
  * libobs/util: Fix *nix CPU core counts
  * libobs: Log *nix system info more like Windows/Mac
  * libobs: Fix XCB keyboard mapping size calculation
  * linux-capture: Watch for VisibilityNotify events
  * libobs: Fix a potential divide by zero crash
  * UI: Allow volume peak to be customized via .qss
  * UI: Fix parent window geometry loading
  * Build with CEF 3112 on OSX
  * obs-browser: version 1.30.1
  * rtmp-services: Update ingest list for Restream.io
  * obs-outputs: Enable FTL logging and reduce verbosity
  * obs-outputs: Fix invalid stream key error
  * rtmp-services: Add new twitch ingest servers
  * obs-outputs: Improve new netcode if encoder reports 0 bitrate
  * rtmp-services: Fixing misspell in a country name
  * vlc-source: Add media control hotkeys
  * rtmp-services: Update ingest list for Restream.io
  * rtmp-services: Add looch.tv streaming platform
  * libobs/util: Add memory usage functions
  * UI: Add memory usage to Stats window on linux/mac
  * libobs: Add Pulseaudio audio monitoring support
  * UI: Enable audio monitoring on linux if pulse available
  * linux-pulseaudio: Use actual sink device names
  * libobs: Fix texture_ready feedback for CPU conversion path
  * libobs: Fix I420 shader for (width/2)%%4 == 2 resolutions
  * libobs: Add private settings to scene items/sources
  * UI: Allow right-clicking mixer sources to bring up menu
  * UI: Allow hiding/unhiding sources in the mixer
  * UI: Add missing option to context menu
  * UI: Use Qt standard buttons in source properties
  * obs-ffmpeg: Don't mark to destroy media unless valid
  * libobs: Fix ImageMagick header path
  * libobs: Stop configure if ImageMagick is preferred, but not found
  * libobs: Adjust grammar of an error message
  * UI: Enable Replay Buffer in Advanced Mode
  * obs-transitions: Add audio monitoring to stinger
  * obs-transition: Add crossfade option to stinger
  * obs-transitions: Fix integer conversion warning
  * UI: Lock graphics context when adding new sources
  * obs-ffmpeg: Fix potential seek issues with media source
  * libobs: Restore Windows Vista compatibility
  * UI/updater: Use TLS 1.2 with WinHTTP
  * libobs: Fix paired audio encoder discarding one segment
  * libobs: Fix starting video packet offset in outputs
  * libobs: Move macro to internal C file
  * obs-outputs: Fix FLV muxing bug
  * libobs: When interleaving packets, make video come first
  * obs-outputs: Fix up the internal FLV output
  * libobs: Set video timing_adjust to obs video time
  * win-capture: Remove buffering from window capture
  * win-wasapi: Subtract frame duration from timestamp
  * test: Add sync tests
  * libobs/media-io: Fix decompress_420 function
  * vlc-video: Set properties to defer update mode
  * graphics-hook: Blacklist specific game from GL capture
  * libobs: Initialize randomization seed in video thread
  * vlc-video: Fix shuffle not being quite that random
  * win-dshow: Fix video playback when default format is MJPEG
  * file-updater: fix crash due to network timeout
  * UI: Log generic stream startup failures
  * libobs: Disable pulseaudio dependency lookup on mac
  * libobs-opengl: Disable v-sync on mac
  * UI: Add ini option to use different graphics adapters
  * libobs/util: Fix Windows 10 revision detection
  * rtmp-services: Only update Twitch ingests when necessary
  * libobs: Add async video/audio decoupling functions
  * decklink: Use unbuffered by default, and decouple
  * obs-outputs: Signal stop if stop called when not active
  * UI: Log when starting / stopping via hotkey or timer
  * UI: Add missing text for replay buffer hotkey log
  * obs-outputs: Only set stop events if still active
  * UI: Disallow pasting duplicates of sources with DO_NOT_DUPLICATE
  * rtmp-services: Don't show "service not found" if name empty
  * UI: Fix Pulse Audio not loading saved device
  * libobs: Update version to 20.1.0
  * Update translations from Crowdin
* Wed Oct 18 2017 jimmy@boombatower.com
- Revert dropping of _service for URL in spec by non-maintainer.
* Sun Oct  8 2017 hillwood@opensuse.org
- Use %%suse_update_desktop_file.
- Fix wrong Group tag.
- Update %%post and %%postun.
- Use URL in Source tag.
- Remove %%clean tag, it's not necessary now.
* Fri Aug 11 2017 jimmy@boombatower.com
- Update to version 20.0.1:
  * UI: Add Studio Mode features in the Frontend API
  * CI: Download deps if they are outdated
  * plugins: Clear warnings about -Wincompatible-pointer-types
  * UI: Add new theme, update theme capabilities
  * .editorconfig: Add file to speed up editor configuration
  * libobs: Fix an int underflow in log_frame_info
  * rtmp-services: Add Chaturbate Streaming Service
  * libobs-d3d11: Fix potential issue rebuilding shared texture
  * UI: Fix potential crash with unsupported video cards
  * vlc-video: Add network caching property
  * libobs-d3d11: Better error message for missing D3DCompiler
  * rtmp-services: Rename beam.pro to Mixer.com
  * vlc-video: Fix integer conversion warning
  * deps/jansson: Update jansson to version 2.9
  * UI: Add fullscreen projector to systray menu
  * UI: Add fullscreen UI option to view menu
  * libobs: Fix bug where obs_data default might not be set
  * UI: Add "Defaults" button to filters/properties windows
  * obs-text: Fix file reader occasionally not updating
  * text-freetype2: Fix file reader occasionally not updating
  * cmake: Add _CRT_NONSTDC_NO_WARNINGS def to all projects
  * UI, libobs: Add ability to lock individual scene items
  * UI, libobs: Add Japanese shortcut keys for Windows
  * rtmp-services: Update servers for Vaughn Live/Breakers.tv
  * libobs/util: Make minor optimization to circlebuf pops
  * libobs: Add <> or \| on RT 102-key as hotkey
  * libobs/plugins/UI: Suppress unused variables warnings
  * UI: Make sure "Defaults" buttons aren't default buttons
  * UI: Make lock/unlock icons slightly smaller
  * UI: Fix lock/visibility sub-widget sizes on OSX
  * obs-qsv11: change re-enter locker implementation
  * decklink: Add feature to detect resolution/format
  * UI: Add ability to drop html files
  * UI: Allow zoom with the scroll wheel
  * win-capture: Log when game capture compatibilty mode is set
  * UI: Remove unused function from volume control
  * libobs: Add obs_volmeter_get_cur_db function
  * UI: Change meter color to red when audio is clipping
  * UI: Add backwards compatible theme fallback
  * rtmp-services: Add LiveEdu (accidentally removed)
  * UI: Ensure theme backward compat. with older OBS vers.
  * obs-filters: Optimize and fix alpha in color grade filter
  * UI: update installer script to latest version
  * rtmp-services: Update twitch.tv ingests
  * UI: Add missing separator in mediaExtensions initializer
  * libobs: Add API to specify codec support on encoded outputs
  * libobs: Add ability for service to specify its output type
  * obs-qsv11, obs-x264: Allow bframe count overriding
  * rtmp-services: Add ability to specify different outputs
  * rtmp-services: Allow services to override bframe count
  * UI: Allow services to use different outputs
  * UI: Allow outputs to use different audio codecs
  * obs-outputs: Fix a few issues with CMakeLists.txt
  * rmtp-services: Don't display warning for invalid file ver.
  * rtmp-services: Fix incorrect RTMP output ID
  * rtmp-services: Update Twitch ingests
  * libobs: Do not save hotkeys for private sources
  * libobs: Add transition callbacks for starting/stopping
  * libobs: Add function to get current transition time
  * libobs: Add ability for transitions to render sources directly
  * obs-ffmpeg: Add proc handler function to get media duration
  * obs-transitions: Add stinger transition
  * rtmp-services: Add Twitter / Periscope as a service
  * UI: Fix problem with exporting scene collections/profiles
  * UI: Add --multi flag to suppress multi-instance warning
  * libobs: Add post-load module callback
  * libobs: Ensure scene items don't have pre-multiplied alpha
  * libobs: Fix item copying during scene duplication
  * rtmp-services: Update Picarto maximum audio bitrate
  * UI: Fix potential crash when outputs change
  * UI: Add "Below Normal" priority option
  * UI: Add modular UI
  * UI: Fix build issue with older linux Qt5 packages
  * UI: Fix settings window minimum width/height
  * libobs: Add API function to get version string
  * deps/file-updater: Add func to get single remote file
  * obs-ffmpeg: Rename obs-ffmpeg-aac.c file
  * obs-ffmpeg: Make FFmpeg audio encoder abstractable
  * obs-ffmpeg: Ensure sample rate is supported in audio encoder
  * obs-ffmpeg: Add Opus audio encoder
  * obs-outputs: Add FTL output
  * rtmp-services: Add Mixer FTL service
  * UI: Update Mixer (formerly Beam) in auto configuration
  * UI: Remove trailing whitespace
  * UI: Return false if audio encoder creation fails
  * rtmp-services: Fix ingest update request user agent
  * rtmp-services: Add Twitch ingest update API
  * rtmp-services: Add "Auto" server option for Twitch
  * UI: Add support for Twitch "Auto" server in auto-config
  * UI: Fix incorrect properties set for Hardware (AMD)
  * rtmp-services: Remove Twtich "Auto" if API down and not cached
  * Revert "UI: Add support for Twitch "Auto" server in auto-config"
  * Revert "libobs: Fix an int underflow in log_frame_info"
  * libobs: Log output frame count instead of encoded count
  * UI: Test first 3 closest Twitch ingests in auto-config
  * UI: Fix Delete key not working on scenes/sources
  * deps/media-playback: Add concat playback support
  * UI: Update Hitbox to Smashcast in autoconfig wizard
  * enc-amf: Update to 2.2.1
  * libobs: Add ability to transition to NULL source
  * image-source: Add 'loop' and 'hide on stop' to slideshow
  * image-source: Add activate/deactivate behavior to slideshow
  * image-source: Add "manual (hotkey)" mode to image slideshow
  * UI: Move adv. audio props. to each audio config button
  * obs-x264: Remove VFR mode as an advanced option
  * vlc-video: Don't allow VLC sources to be cloned
  * rtmp-services: Update Switchboard ingests
  * UI: Fix stats window geometry saving on shutdown
  * UI: Show error if empty recording path specified
  * libobs: Export obs_output_get_last_error
  * obs-ffmpeg: Improved output error handling
  * UI: Report more detailed output errors if available
  * UI: Show error if empty recording path specified
  * obs-ffmpeg: Add proc handler for getting number of frames in video
  * obs-transitions: Add frame transition point option to stinger
  * obs-transitions: Fix stinger transition locale
  * obs-outputs: Change loglevel of ftl status thread to debug
  * enc-amf: Update to 2.2.2
  * UI/updater: Restart progress bar when installing updates
  * UI/updater: Improved handling of failure conditions
  * libobs: Update version to 20.0.0
  * rtmp-services: Initialize mutex/dynamic array
  * rtmp-services: Require cmake var to enable ingest updates
  * obs-transitions: Rename stinger ID to prevent conflict
  * Update translations from Crowdin
  * rtmp-services: Always check service updates on non-windows
  * image-source: Fix potential crash with slideshow
  * UI: Fix conditions for redraw the stats labels
  * libobs: Update version to 20.0.1
  * libobs: Add default hotkey id to duplicated item
  * UI: Fix Stats not showing stream data until start
* Thu Jun 22 2017 jimmy@boombatower.com
- Update to version 19.0.3:
  * rtmp-services: Update Twitch ingests
  * librtmp: Fix build error with ENODATA on FreeBSD
  * rtmp-services: Rename Beam to Mixer
  * UI/installer: Specify "source" in plugins section
  * UI/installer: Fix broken realsense plugin install locations
  * UI/installer: Update installer VC redist download link
  * win-wasapi: Fix potential null pointer deref in enumeration
  * UI: Look for plugins in ~/Library/Application Support/obs-studio/plugins/
  * libobs/plugins/UI: Suppress -Wimplicit-fallthrough introduced by GCC 7
  * win-capture: Limit OpenProcess flags to prevent A/C issues
  * deps/media-playback: Output av_read_frame error string
  * deps/media-playback: Start decoding regardless of keyframe
  * obs-ffmpeg: Add network buffering property
  * deps/media-playback: Call stop callback on failure
  * deps/media-playback: Fix lockup issues
  * Revert "rtmp-services: Rename Beam to Mixer"
  * rtmp-services: Add new twitch.tv ingests
  * UI/updater: Fix incorrect path in portable mode
  * deps/media-playback: Add timeout when waiting for frames
  * deps/media-playback: Fix AV_NOPTS_VALUE being used as timestamp
  * deps/media-playback: Fix playback reset fail after stop
  * obs-ffmpeg: Don't preload media frames if set to pause on end
  * win-capture/graphics-hook: Fix D3D10/D3D11 detection
  * UI: Ignore first 2.5 seconds of bandwidth test
  * UI: Initialize Stats window values after OBSInit/reset
  * win-capture: Add IDXGISwapChain1::Present1 hook support
  * win-capture: Use PROCESS_QUERY_INFORMATION for game capture
  * obs-ffmpeg: Do not precache if set to close when inactive
  * UI: Use QT_TO_UTF8 with name dialog
  * libobs-d3d11: Fix shader const array size miscalculation
  * UI: Preserve source if audio settings device changed
  * libobs: Update version to 19.0.3
  * UI: Set error mode to SEM_FAILCRITICALERRORS
  * ffmpeg-mux: Set error mode to SEM_FAILCRITICALERRORS
  * get-graphics-offsets: Set error mode to SEM_FAILCRITICALERRORS
  * inject-helper: Set error mode to SEM_FAILCRITICALERRORS
  * enc-amf: Version 2.1.6
  * obs-ffmpeg: Remove "Buffering (MS)" property
* Wed Jun 14 2017 jimmy@boombatower.com
- Update to version 19.0.2:
  * UI: Fix drag & drop bug
  * frontend-tools: Add automatic scene switcher for Linux
  * UI: Add option to disable audio ducking on windows
  * rtmp-services: Update ingests
  * libobs/util: Add Get function to BPtr<>
  * UI, obs-qsv11: Fix build in VisualStudio 2017
  * UI: Fix warning in VisualStudio 2017
  * obs-qsv11: Fix SEI crash caused by dangling pointer
  * UI: Add ability to output to window
  * UI: Always alternatively open backup scene json file
  * libobs: Don't call unlink unnecessarily
  * libobs/util: Add os_safe_replace function
  * libobs/util: Use os_safe_replace in safe file writes
  * libobs/util: Flush text files when writing
  * libobs/util: Use MoveFileEx with MOVEFILE_REPLACE_EXISTING
  * vlc-video: Add ability to shuffle playlist in VLC source
  * Various: Optimize bundled PNG files
  * text-freetype2: Make font lookup recursive on mac
  * libobs: Use tex.Load for reverse NV12/I420 funcs
  * UI: Fix settings dialog crashing on linux
  * libobs: Fix tex.Load lookup (needs int3, not int2)
  * libobs: Add random shader
  * libobs: Fix skipped frames reporting
  * libobs: Add functions to get logical/physical cores
  * libobs: Pass exact data when calling obs_get_video_info
  * libobs: Add function to allow custom output drawing
  * libobs: Add function to allow getting output connect time
  * libobs: Don't allow lagged frames to be counted as skipped
  * obs-outputs: Add null output
  * obs-outputs: Add connect time callback for rtmp output
  * obs-outputs: Fix frame dropping when using ultrafast
  * UI: Add function to enable/disable outputs
  * UI: Don't subject base/output resolutions defaults
  * UI: Limit default canvas res to 1920x1080 or below
  * UI: Add 1920x1080/1280x720 to the settings base res list
  * UI: Remove colon from a few locale items
  * UI: Add auto-configuration wizard
  * CI: OSX - Use wget instead of curl
  * libobs: Fix os_safe_replace not working linux
  * UI: Show invalid Bind to IP entries in the settings
  * decklink: Fix compiler warning about ignored const
  * decklink: Add option to disable the plugin
  * decklink: Remove unused variables to fix warning
  * win-capture: Hide cursor when in background (game capture)
  * Various: Don't use boolean bitfields
  * win-capture: Hide cursor when in background (window capture)
  * rtmp-services: Rename hitbox.tv to Smashcast
  * obs-ffmpeg: Add signal/proc to restart media playback
  * CI: exclude .gitignore
  * CI: Use git fetch --unshallow for OSX
  * libobs/util: Add function to get free disk space
  * libobs-opengl: Fix potential crash w/ viewports
  * libobs: Add function to get average render time
  * libobs: Add functions to get total/lagged frames
  * libobs: Add obs_output_reconnecting func
  * obs-ffmpeg: Implement get_total_bytes in recording outputs
  * UI: Add function to get current memory usage (win32)
  * UI: Add themeID values for colors to style sheets
  * UI: Add stats dialog
  * UI: Fix a few locale items, and add a few missing ones
  * UI: Make Qt use locale text for QWizard buttons
  * UI: Add helper class to translate message box buttons
  * UI: Make sure all message box buttons are translated
  * UI: Fix locale text for "OK" in question dialogs
  * UI: Bring stats to front if it already exists
  * UI: Add option to show stats on startup to general
  * UI: Save/remember stats window geometry
  * Revert "libobs: Allow source to fully control source flags (for now)"
  * libobs: Don't use source flags for async buffering
  * UI: Don't use "quit on last window closed"
  * UI: Fix bug where Pre19Defaults would always be set
  * UI: Don't count debug log messages in repeat detection
  * UI: Warn user if multiple instances of the UI are open
  * enc-amf: Version 2.1.3
  * image-source: Allow custom bounding source size/aspect
  * UI: Update quick transitions on transition add/removal
  * libobs: Add scene item IDs
  * win-dshow: Update libdshowcapture to 0.5.12
  * UI: Add support for showing output error messages
  * libobs: Add support for output error messages
  * obs-outputs: Add output error messages for RTMP
  * UI: Fix misleading log message when updating settings
  * UI: Change output blocking bool to integer ref counter
  * UI: Prevent user from starting ouputs while in settings
  * UI: Move Stats to the view menu
  * UI: Make Stats a regular window rather than dialog
  * UI: Check to see if outputs valid when updating stats
  * deps/media-playback: Remove unnecessary logging
  * UI: Fix creation of log files with non-english paths
  * libobs-d3d11: Only load vertex buffer before drawing
  * deps/media-playback: Include SSE flags
  * deps/media-playback: Do not seek network streams
  * deps/media-playback: Init avformat in thread
  * obs-ffmpeg: Only preload frames for local files
  * obs-ffmpeg: Always close network sources when inactive
  * libobs: Update to version 19.0.0
  * libobs: Make obs_source_default_render exported
  * obs-filters: Add Render Delay filter
  * UI: Sort filter names when adding filters
  * deps/media-playback: Discard packet returns of invalid sizes
  * deps/media-playback: Use new FFmpeg decode funcs when possible
  * deps/media-playback: Always check for new frame first
  * UI: Fix cases where wizard bitrate is not capped
  * UI: Remove advanced settings from final wizard results
  * UI: Actually update service for wiz. bitrate limits
  * UI: Fix enumeration of scene collections on first run
  * obs-ffmpeg: Disable media source HW accel. for now
  * libobs: Do not allow incompatible filters on sources
  * rtmp-services: Preserve settings if service renamed
  * obs-filters: Increase allowable render delay to 500ms
  * enc-amf: Version 2.1.4
  * VST: bump vst submodule ref
  * Update translations from Crowdin
  * UI: Change default autoconfig test bitrate
  * AUTHORS: Update with data from Git and Crowdin
  * deps/media-playback: Fix bug where inverted media would crash
  * UI: Remove whitespace from end of autconfig stream key
  * libobs/util: Also remove CR/LF from dstr_depad
  * UI: Fix bug where auto-config settings wouldn't apply
  * Fix German locale inconsistencies
  * libobs: Always call stop callback
  * UI: Unlock mutex before trying to stop output
  * libobs: Fix bug where outputs would not set stopped event
  * libobs: Update version to 19.0.1
  * enc-amf: Version 2.1.5
  * UI: Fix creation of crash log with non-english paths
  * libobs-d3d11: Fix bug where vertex buffers would be reset
  * UI: Fix autoconfig capping bitrate with "custom server"
  * libobs: Update to version 19.0.2
  * Revert "obs-ffmpeg/nvenc: Remove "default" preset"
  * UI: Fix tooltip for "prefer hardware encoding"
* Tue May  2 2017 jimmy@boombatower.com
- Update to version 18.0.2:
  * UI/updater: Fix temp files being created and not deleted
  * UI/updater: Fix potential fail case when no files to patch
  * UI/updater: Fixed a bug with deflating
  * UI/updater: Ignore 64bit files on 32bit windows
  * CI: Use ccache to speed up the build
  * CI: OSX - Fix obs.png
  * UI/updater: Fix incorrect inflate use
  * CI: Linux - Install libfdk-aac-dev
  * image-source: Move file modification check before animation processing
  * UI: Add workaround to fix deleting final scene bug
  * rtmp-services: Update ingest list for Restream.io
  * rtmp-services: Update maximum bitrate for Twitch
  * UI: Fix segfault when no system tray exists
  * CI: Linux - Install FFmpeg from source
  * obs-ffmpeg/nvenc: Remove "default" preset
  * libobs: Add obs_source_copy_filters function
  * UI: Add copying/pasting of sources/filters
  * UI: Disable filter pasting when scene collection changed
  * UI: Fix bug where items can't be deleted in last scene
  * libobs: Remove unimplemented exports
  * rtmp-services: Add Livestream service
  * win-dshow: Fix issue with activating when not set to
  * rtmp-services: Update Picarto maximum bitrates
  * libobs: Delay stop detection of audio source
  * libobs: Allow source to fully control source flags (for now)
  * libobs: Add ability to preload async frames
  * libobs: Remove multiple calls to free_type_data
  * deps: Add media-playback static lib
  * obs-ffmpeg: Change from libff to media-playback
  * deps/libff: Remove network init
  * UI: Remove libff as a dependency
  * deps/libff: Don't build libff (deprecated)
  * obs-ffmpeg: Remove unnecessary open call
  * obs-ffmpeg: Always open on update unless set otherwise
  * obs-ffmpeg: Fix bug on non-MSVC compilers
  * UI: Fix property widgets not being disabled
  * mac-avcapture: Ability to directly add iOS devices over USB
  * audio-monitoring: Add ability to monitor Outputs
  * decklink: Add option to select channel format
  * decklink: Add workaround for audio timestamp jump issue
  * Improve README/CONTRIBUTING files
  * win-dshow: Fix reallocation issue in ffmpeg-decode
  * UI: Add window name to remux dialog
  * UI: Hide OpenGL and D3D adapter on Windows
  * UI: Continue to show OpenGL if already in use
  * UI: Increase MAX_CRASH_REPORT_SIZE to 150 KB
  * CI: Use webhooks for notifications
  * CI: Fix notification frequency
  * libobs-opengl: Log OpenGL version on all systems
  * Fix various typos across multiple modules
  * Update Linux kernel coding style URL in CONTRIBUTING
  * UI: Ctrl+E to Edit Transform
  * UI: Remove unused defines from old updater code
  * win-capture: Log if shared texture capture is unavailable
  * win-capture: Update get-graphics-offsets
  * win-capture: Add missing 32 bit offsets
  * win-capture: Fix and clarify window capture prioritization
  * UI: Add front-end API functions to get/modify service
  * UI: Display filename when dragging & dropping
  * obs-outputs: Always call RTMP_Init before connecting
  * UI: Make sure all dialogs have close buttons
  * UI: Add command line option for starting up always on top
  * frontend-tools: Rename some files
  * frontend-plugins: Abstract captions
  * enc-amf: Update to v2.1.0(.0)
  * win-ivcam: Fix potential null pointer dereference
  * libobs: Update to 18.0.2 (windows hotfix)
  * UI/updater: Add opt to disable building update module
* Tue Mar  7 2017 jimmy@boombatower.com
- Update to version 18.0.1:
  * CI: Fix true / false on stable builds
  * CI: Add boolean arg parser to OSX
  * CI: Deploy on tags and master branch
  * CI: OSX - Deploy on all branches in the master repo.
  * CI: OSX - Include branch in pkg
  * enc-amf: Update to 1.4.3.11
  * UI: Use correct string for systemTrayEnabled
  * CI: OSX - Update to CEF 2987
  * CI: Use correct folder for building browser
  * CI: OSX - Use bash variable for CEF version
  * UI: Don't exit on unknown command line arguments
  * CI: OSX - export cef version so we can use it elsewhere
  * CI: Fix cef version variable
  * obs-outputs: Fix 100%% CPU usage with new network code
  * CI: OSX - Move CEF version to .travis
  * VST: Fix save / load of plugin state. More interface options.
  * UI: Fix audio monitoring dev. not being set on startup
  * UI: Log audio monitoring dev. on start and when changed
  * UI: Add logging of audio monitoring to sources
  * VST: Fix crash when OBS is set to mono
  * Revert "win-dshow: Add LGP timestamp fix"
  * win-dshow: Actually fix LGP issue
  * obs-outputs: Various fixes to new network code
  * Update translations from Crowdin
  * AUTHORS: Update with data from Git and Crowdin
  * libobs: Apply sync offset to win32 audio monitoring
  * UI: Disable network settings while outputs active
  * Update translations from Crowdin
  * AUTHORS: Update with data from Git and Crowdin
  * CI: OSX - Brew install speexdsp
  * CI: OSX - enable sparkle
  * deps/blake2: Fix compiler warning
  * UI: Fix game capture check when about to update
  * deps: Add liblmza
  * libobs: Update to 18.0.1
  * updater: Add windows updater module
  * UI/updater: Wait for OBS to close before updating
  * obs-outputs: Improve shutdown behavior of new socket loop
  * UI/updater: Use better function for getting process names
* Tue Feb 28 2017 jimmy@boombatower.com
- Update to version 18.0.0:
  * UI: Add more command line options
  * obs-browser: Update submodule to latest version
  * Revert "Revert "win-capture: Use FindWindowEx to traverse window list""
  * CI: Add in inital appveyor config
  * CI: Move browser source before building app
  * CI: Build VLC plugin for OSX on travis
  * rtmp-services: remove shut down services
  * CI: Build Windows version and upload artifacts
  * obs-browser: Update browser ref
  * CI: Update permissions on CEF app plist before packaging
  * cmake: Enable COPY_DEPENDENCIES by default on Windows
  * rtmp-services: Update Vaughn Live ingests
  * libobs: Log correct amount of memory on 32bit (windows)
  * UI: Convert to wide before outputting debug text (win)
  * UI: Protect debug text static string var with mutex
  * libobs: Add ability to get output congestion
  * obs-output: Add ability to get congestion to rtmp output
  * obs-outputs: Increase default drop threshold
  * UI: Add connection status square to status bar
  * UI: Add separate timers to status bar
  * UI: Add option to always minimize to tray
  * UI: Hide/show dialogs when minimizing to tray
  * UI: Do not quit program when last windows are projectors
  * UI: Add option to save projectors
  * UI: Add auto-start replay buf. opt. when stream starts
  * UI: Fix scaling in viewport when source flipped
  * UI: Fix linux display/resize bug with preview widget
  * rtmp-services: Add Restream.io Los Angeles server
  * libobs: Add optional ultrawide -> wide scaling techniques
  * obs-filters: Add option to undistort ultrawide -> wide
  * obs-filters: Add "Color Grading" filter
  * rtmp-services: Add new beam.pro ingests
  * CI: Add post install script to OBS installer to fix CEF permissions
  * rtmp-services: Add Web.TV streaming service
  * Add VST Plugin
  * obs-filters: Fix compiler warnings
  * UI: Remove unused variables
  * UI: Clarify "Always minimize to tray" option
  * obs-filters: Rename "Color Grade" filter to "LUT Filter"
  * obs-filters: Change "LUT Filter" to "Apply LUT"
  * CI: Fix VLC download
  * CI: Unzip VLC quietly
  * rtmp-services: Update twitch/hitbox ingest and youtube recommendations
  * CI: Fix OSX post-install script
  * UI: Fix locale text alignment
  * UI: Make advanced settings pane a bit more compact
  * libobs: Mark last video ts even when buffering off
  * libobs: Mark parameter as constant if not modifying
  * libobs: Use original audio structure for audio signal
  * libobs: Implement audio monitoring
  * win-wasapi: Mark audio outputs as unmonitorable
  * UI: Add audio monitoring to settings/adv audio props.
  * UI: Prevent thread stalls with fader/volume widgets
  * obs-transitions: Convert premultiplied alpha to straight
  * UI: Add 24 NTSC as a common FPS value
  * obs-ffmpeg: Do not use HW accel by default on mac
  * rtmp-services: Update twitch ingests
  * obs-ffmpeg: Fix compiler warnings
  * UI: Fix compiler warning
  * UI: Change volume meter update interval to 30fps
  * UI: Add warning if starting the output fails
  * obs-ffmpeg: Be more verbose when custom params fail
  * obs-ffmpeg: Fix custom audio codec parameters
  * CI: Retry failed downloads
  * UI: fix ffmpeg output file extension
  * UI: Clean up general pane of settings dialog
  * UI: Add function to get remote file
  * UI: Add front-end auto-updater
  * UI: Update installer to latest version
  * UI: Add latest installer fixes from R1CH
  * obs-ffmpeg: Add 'save' to replay buffer proc handler
  * win-capture: Fall back to GetWindow if FindWindowEx fails
  * libobs: Fix audio monitoring delaying perpetually
  * rtmp-services: Update max video bitrate for beam
  * libobs/util: Use a mutex with config files
  * win-capture: Blacklist chrome/firefox from game capture
  * win-dshow: Add LGP timestamp fix
  * UI: Trigger frontend api scene change after transition
  * Add AUTHORS file
  * mailmap: Disambiguate between a few authors
  * mailmap: Disambiguate between another author
  * rtmp-services: Add "Pandora TV Korea"
  * UI: Trigger scene list change event when scene removed
  * CI: Speedup msbuild by using all CPU cores
  * UI: Improve accessibility text on main window
  * CI: Download VLC repo instead of cloning from git
  * CI: Disable test discovery on AppVeyor
  * CI: Cache dependencies downloads on AppVeyor
  * CI: Disable deps download in AppVeyor and use cache
  * CI: Download deps if they aren't in build cache
  * UI: Use blake2b instead of SHA1 for updater
  * UI: Make installer execute 64bit on 64bit windows
  * obs-text: Fix issue drawing some chinese characters
  * obs-filters: Add audio compression filter
  * obs-outputs: Port windows socket loop from OBS Classic
  * librtmp: Clean up our extra RTMP fields on close
  * UI: Add options for new socket loop
  * UI: Make sure size-specific spacers are fixed
  * UI: Fix some settings layouts on non-windows systems
  * win-capture: Add hook exception for theHunter: COTW
  * obs-ffmpeg/ffmpeg-mux: Fix failing when no video
  * image-source: Add solid color source
  * image-source: Add missing locale
  * Fix various null pointer issues detected by Coverity
  * obs-ffmpeg: Allow saving with different video codecs
  * UI: Add support for other codecs
  * graphics-hook: Account for sizeof(wchar_t) in len
  * obs-qsv11: Fix various issues detected by Coverity
  * obs-ffmpeg: Make gop size configurable
  * UI: Add gop size option for custom ffmpeg output
  * libff: Add override for codec compatability check
  * UI: Add codec compatability checkbox to ffmpeg output
  * UI: Add warning about recording to mp4 format
  * CI: Fetch git tags on OSX build
  * CI: Exit on errors when building the OSX package
  * UI: Fix typo in general settings
  * enc-amf: Update to version 1.4.3.9
  * CI: Build on Linux
  * libobs: Update version to 18.0.0
  * libobs: Fix bug where scenes would not properly mix audio
  * UI: If scene/source names exist, start from 2
  * CI: Don't skip_join for Travis IRC notifications
  * obs-frontend-api: Use virtual destructor (fix memory leak)
  * libobs: Add missing mutex unlock in audio monitoring
  * CI: Get some codesigning and sparkle stuff in place
  * CI: Use combined cert for signing OSX
  * CI: Set keychain timeout & allow productsign
  * CI: Add some logging to the before deploy script on OSX
  * CI: Possibly fix OSX cert import issue
  * CI: OSX - Brew install jack
  * CI: Notify on failure and only for fixed builds
  * CI: Reformat Travis CI IRC notification
  * UI: Hide auto update option for linux
  * obs-filters: Change attack/release ms limit to 300 (from 100)
  * obs-filters: Increase max compressor release/attack values
  * Update translations from Crowdin
  * AUTHORS: Update with data from Git and Crowdin
  * UI: Update Simple Mode AMD Presets
  * enc-amf: Update to hotfix 1.4.3.10
  * CI: OSX Set builds to stable on tagged builds
  * CI: Update public OSX install key
* Wed Jan 18 2017 jimmy@boombatower.com
- Update to version 17.0.2:
  * libobs: Update to 17.0.2
* Tue Jan 17 2017 jimmy@boombatower.com
- Update to version 17.0.1:
  * deps/libff: Fix VP8/VP9/webm alpha support
  * rtmp-services: Increase video bitrate limit for YouTube
  * obs-outputs: fix build error on freebsd
  * Update translations from Crowdin
  * [CI] Use prebuilt deps so we can build on 10.9
  * CI: Build more features into FFMPEG deps
  * CI: Update browser plugin ref and build scripts.
  * CI: Fix zip permission issue on CEF plist files
  * obs-x264: ignore opencl param
  * enc-amf: Update to 1.4.3.8
  * CI: Ability to make packages on travis
  * CI: actually call packagesbuild from the right place 😑
  * cmake: Remove unnecessary find_package calls
  * libobs: Fix scale filtering bug when duplicating scenes
  * win-capture: Don't use FindWindow for game capture keepalive
  * CI: Install Packages and use the full version
  * Revert "win-capture: Use FindWindowEx to traverse window list"
  * obs-filters.c: Fix color correction filter OpenGL crash
  * obs-filters.c: Fix color correction filter saturation
  * Update translations from Crowdin
  * UI: Fix bug with uncopied profile import/export files
  * win-capture: Fix game capture size bug when rehooking
  * libobs: Add func to enum active and inactive child tree
  * libobs: Enumerate full tree when adding active child
  * libobs: Add callback for enumerating all scene children
  * obs-x264: Allow opencl through much longer alias
  * libobs: Update to version 17.0.1
* Mon Dec 26 2016 jimmy@boombatower.com
- Update to version 0.17.0:
  * rtmp-services: Update ingest list for Restream.io
  * Revert "CI: Build on OSX 10.10 on travis"
  * Remove python dep
  * win-capture: Use static runtimes for hooks/helpers
  * cmake: Fix OSX fixup_bundle.sh to copy non-system deps
  * cmake: Fix permissions with OSX fixup_bundle.sh
  * libobs-opengl: Add xcb message poll to empty out the queue
  * frontend-tools: Add options to start output timers every time
  * libobs-d3d11: Add optional macro to log shader disassembly
  * Revert "obs-transitions: Avoid branching in slide_transition.effect"
  * rtmp-services: remove shut down services
  * libff: Allow custom demuxer options
  * obs-outputs: Fix librtmp IP bind / resolve behavior
  * UI: Fix frontend-api event call for adding scenes
  * libobs/util: Add function to get circlebuf data offset
  * libobs/util: Add function to generate formatted filenames
  * libobs: Fix bug where outputs cannot initialize hotkeys
  * cmake: Add _CRT_SECURE_NO_WARNINGS to all projects
  * libobs: Fix deprecated macro
  * libobs/util: Do not ignore deprecation on windows
  * libobs: Use reference counting for encoder packets
  * obs-ffmpeg: Add replay buffer output
  * UI: Disable simple output rec. settings when active
  * UI: Add replay buffer options to simple output mode
  * UI: Clarify replay buf. hotkey error message
  * UI: Separate replay buffer from recording
  * UI: Add file prefix/suffix options for replay buffer
  * UI: Fix replay buffer compile issues on older compilers
  * win-capture: Only duplicate to get cur thread handle
  * win-capture: Always use minimal access rights within hook
  * win-capture: Do not require pipe/mutex within hook
  * win-capture: Fix getting proper UWP window handles
  * win-capture: Use window for keepalive check
  * win-capture: Create all named objects within hook
  * win-capture: Don't use "Local\" for game capture shared mem
  * win-capture: Remove redundant function
  * win-capture: Use wide strings for named objects
  * win-capture: Add ability to open UWP named kernel objects
  * win-capture: Open UWP named objects with helper functions
  * win-capture: Output hook debug messages if addresses missing
  * win-capture: Log plugin-side when capture successful/lost
  * win-capture: Don't hook suspended processes
  * win-capture: Wait a few frames for hook to load
  * win-capture: Fix "attempting to hook [executable]" message
  * win-capture: Add ApplicationFrameHost to game capture blacklist
  * win-capture: Don't hard fail if thread ID not found
  * win-capture: Fix cursor not painting with UWP windows
  * win-capture: Add debug messages when hooking
  * win-capture: Do not fall back to other windows for UWP windows
  * UI: Fix property name bug in frontend API
  * libobs: Fix possible reverse order mutex hard lock
  * UI: Remove deleteLater view from filter window layout
  * libobs: Convert Y800 to RGBX manually
  * UI: Use dedicated GPU on Hybrid AMD GPU systems
  * libobs: Fix format not being set for new source frames
  * libobs: Fix line size issue when copying Y800 data
  * obs-ffmpeg: Don't allow 32kb/s with FFmpeg AAC encoder
  * libobs/graphics: Fix the 2D vector dot product func
  * UI: Make close button default in transform dialog
  * UI: Add ability to copy-paste scene item transforms
  * UI: Add import/export of scene collections & profiles
  * enc-amf: Update to 1.4.3.4 for AMD Driver 16.12.1
  * obs-filters: Improve "Color Correction" filter
  * image-source: Do not change blend state
  * obs-text: Do not reset blend state
  * libobs-d3d11: Don't crash if unable to rebuild shared texture
  * libobs: Increase maximum audio tracks to 6
  * UI: Increase maximum audio tracks to 6
  * UI: Update locale for 6 tracks
  * UI: Fix endif in installer
  * UI: Use 64bit desktop link by default in installer
  * UI: Clarify startup error messages related to video
  * obs-ffmpeg: Fix nvenc_h264 deprecated message
  * libobs: Fix bug drawing RGB/BGR async sources
  * libobs: Process all scene audio actions if no audio playing
  * UI: Fix buddy controls with new audio tracks
  * UI: Add default audio track bitrates
  * UI: Fix video initialization failure error message
  * UI: Fix settings window stacked widget index
  * win-capture: Capture all D3D12 backbuffers
  * win-capture: Use FindWindowEx to traverse window list
  * win-capture: Fix possible null pointer dereference
  * win-capture: Do not add certain windows to window lists
  * win-capture: Add a few new blacklisted game capture exes
  * obs-filters: Add "Color" option to color correction filter
  * obs-filters: Fix comment messages
  * obs-qsv11: Use d3d9 allocator on Win7
  * win-capture: Fix possible access of array beyond size
  * win-capture: Refactor DX12 backbuffer code
  * win-capture: If backbuffer count is 1, disable dxgi 1.4 use
  * win-capture: Release backbuffers immediately upon init
  * libobs/util: Fix C++ compilation issue
  * Add libcaption library
  * libobs: Add ability to insert captions into frames
  * frontend-tools: Move source helper functions to a header
  * frontend-tools: Add caption generation tool (windows)
  * Update translations from Crowdin
  * frontend-tools: Add ability to select caption language
  * frontend-tools: Detach caption thread if critical failure
  * frontend-tools: Reset stop event before starting captions
  * frontend-tools: Don't include colon in "Audio Source"
  * frontend-tools: Set buddied controls for captions dialog
  * libobs: Fix caption encoder packet reallocation
  * libobs: Create referenced parsed AVC encoder packet
  * obs-outputs: Free encoder packet data manually
  * libobs: Fix bug in AVC encoder packet allocation
  * UI: Fix Export QFileDialog parent
  * libobs: Eliminate an unnecessary allocation with captions
  * frontend-tools: Fix output-timer translation bug
  * libobs: Update to version 17.0.0
* Mon Nov 21 2016 jimmy@boombatower.com
- Update to version 0.16.6:
  * UI: Add --verbose and --unfiltered_log command line options
  * libobs: Duplicate filters of a scene when it is is duplicated
  * obs-ffmpeg: Fix assumption about plane height with i444
  * libobs: Refactor check for Windows bitness/arch
  * libobs: Add Windows bitness/arch to crash handler
  * enc-amf: Update to version 1.4.1.5
  * UI: Add preview scaling options
  * rtmp-services: Change YouTube keyint from 4 to 2
  * libobs: Ensure async source sizes are always reset
  * UI: Fix crash when switching encoders in advanced mode
  * UI: Fix scrolling while preview is locked
  * libobs: Ensure AVC priority is always highest for keyframes
  * obs-outputs: Use correct variable for drop priority
  * enc-amf: Update to commit which prevents crash on startup
  * enc-amf: Update to temporary fix branch
  * win-capture: Do not load 64bit hook offsets on 32bit systems
  * win-capture: Defer hook offset loading to separate thread
  * text-freetype2: Defer loading of plugin until source created
  * obs-qsv11: Manually mark priority bits for QSV frames
  * Revert "libobs: Ensure AVC priority is always highest for keyframes"
  * libobs: Update to 0.16.6
  * Update translations from CrowdIn
  * UI: tray icons are redrawn for better visibility and contrast
  * UI: Update settings and fix presets for simple AMD encoder
  * enc-amf: Update to 1.4.2.2
  * enc-amf: Update to 1.4.2.3
  * cmake: Add module to find RSSDK
  * cmake: Add macro to compile .tlb files via midl
  * win-ivcam: Add Intel RealSense plugin
  * UI: Update installer script to latest version
  * libobs-opengl: Add warning when used on windows
  * Update translations from Crowdin
  * enc-amf: Avoid using C++17 for VS2013 compatibility
* Tue Nov  8 2016 jimmy@boombatower.com
- Update to version 0.16.5:
  * libobs-d3d11: Include GDI surface in rebuild
  * libobs-d3d11: Remove possible null pointer dereference
  * libobs: Update to 0.16.5
* Fri Nov  4 2016 jimmy@boombatower.com
- Update to version 0.16.4:
  * libobs/util: Fix get_dll_ver not reporting DLL name
  * Display license in MSI installer
  * rtmp-services: Add Asian Livecoding.tv server and increase video bitrate
  * UI: Enable HiDPI scaling.
  * frontend-tools: Fix crash when adding invalid regex
  * UI: Use Qt lib for screen info instead of x11 libs
  * enc-amf: Update to 1.3.2.3
  * UI: Only scale HiDPI on QT 5.6+
  * enc-amf: Update to 1.3.3.1
  * libobs-d3d11: Log GetDeviceRemovedReason
  * Add 256x256 icon to windows ico for HiDPI displays
  * UI: Add Portable Mode indicator to title bar and log
  * UI: Add raw text and text file to drag&drop support
  * UI: Split Properties window with a QSplitter
  * CMake: Warn if empty QTDIR/DepsPath vars on Windows
  * OSX Travis build
  * CI: Upload artifacts on all pushes
  * CI: Add irc notifications to travis config
  * CI: Reduce travis irc notice to one line
  * CI: Package OSX build into an actual app
  * CI: Use python2 to run package script
  * Build browser plugin on travis for OSX
  * Update obs-browser submodule to a working version
  * obs-frontend-api: Add library version
  * cmake: Fix FFmpeg search path on debian
  * decklink: Update Blackmagic SDK to 10.8.0
  * CI: Build on OSX 10.10 on travis
  * UI: Fix bug in frontend API event
  * frontend-tools: Add output timers
  * frontend-tools: Code cleanup of output timers
  * frontend-tools: Add ability to start timer if output is already active
  * UI: Fix sys. tray crashes when sys. tray not available
  * UI: Fix poor handling of system tray pointers
  * UI: Fix improper brace placement for function
  * UI: Remove unused variable
  * UI: Fix full screen projector on screens that have reserved areas
  * obs-ffmpeg: Add b-frames to NVENC logging
  * UI: Fix --profile option not working on non-windows
  * rtmp-services: Add Picarto
  * libobs/util: Add Get() function to CoTaskMemPtr
  * libobs: Fix missing call to profile_end() when encoding fails
  * libobs: Add date/time to crash handler
  * obs-transitions: Avoid branching in slide_transition.effect
  * obs-ffmpeg: Fix a couple printf compiler warnings.
  * libobs-d3d11: Store dxgi adapter used for device
  * libobs-d3d11: Store compiled shader data (for rebuilding)
  * libobs-d3d11: Correct error message for pixel shaders
  * libobs-d3d11: Store shader samplers as pointers
  * libobs-d3d11: Correct error message for staging surfaces
  * libobs-d3d11: Correct error message creating blend states
  * libobs-d3d11: Store index and add "Start" function
  * libobs-d3d11: Clear device state before unloading
  * libobs-d3d11: Store swap initialization data (for rebuilding)
  * libobs-d3d11: Store device adapter index (for rebuilding)
  * libobs-d3d11: Store static textures in RAM (for rebuilding)
  * libobs-d3d11: Store static vertex buffer data (for rebuilding)
  * libobs-d3d11: Save all D3D11 object descriptors (for rebuilding)
  * libobs-d3d11: Make shared texture error message less vague
  * libobs-d3d11: Use linked list for all objects (for rebuilding)
  * libobs-d3d11: Remove unused function
  * libobs-d3d11: Add Release funtions to all GS objects
  * libobs-d3d11: Rebuild device and assets if device removed/reset
  * win-capture: Cache cursor textures to prevent reallocation
  * win-capture: Use IUnknown for getting swap backbuffers
  * win-capture: Add D3D12 capture support
  * UI: Allow the ability to use deprecated sources
  * UI: Add AMD presets and update settings
  * enc-amf: Update to release 1.4.0.0
  * Update translations from CrowdIn
  * libobs: Update to version 0.16.3
  * win-mf: Deprecate AMD Media Foundation H.264 encoder
  * UI: Fix tab order of Crop fields in Transform Properties
  * enc-amf: Update to Version 1.4.1.0
  * Revert "UI: Only scale HiDPI on QT 5.6+"
  * Revert "UI: Enable HiDPI scaling."
  * enc-amf: Fix VS2013 compiling issue
  * libobs: Update to version 0.16.4
- Expand libobs-frontend-api.so to include all versions in %%files.
- After upstream fix place libobs-(opengl|frontend-api).so in devel.
* Thu Sep 29 2016 jimmy@boombatower.com
- Update to version 0.16.2:
  * obs-ffmpeg: Fix possible NVENC crash
  * UI: Use rect intersection test for validating position
  * enc-amf: Update submodule to 1.3.1.0
  * obs-text: Add gradient feature
  * enc-amf: Fix warnings caused by warnings( push/pop )
  * libobs: Update to 0.16.2
* Thu Sep 29 2016 jimmy@boombatower.com
- Update to version 0.16.1:
  * UI: Fix window size/pos not saving on exit
  * libobs/util: Fix fread_utf8 not working with files < 3 bytes
  * obs-text: Change file update interval to 1 sec (from 2)
  * libobs: Update to 0.16.1
* Wed Sep 28 2016 jimmy@boombatower.com
- Update to version 0.16.0:
  * enc-amf: Update submodule to 1.3.0
  * UI: Add media/image file drop support
  * enc-amf: Update submodule to 1.3.0.1
  * obs-browser: Add browser plugin as a submodule
  * enc-amf: Update submodule to 1.3.0.3
  * libobs: Update version to 0.16.0
  * enc-amf: Remove unused locale files
  * Update translations from Crowdin
  * UI: Just use 'OK' button for license agreement dialog
* Mon Aug  8 2016 jimmy@boombatower.com
- Update to 0.15.4 release.
* Sat Jul 16 2016 jimmy@boombatower.com
- Update to 0.15.2 release.
* Tue Jul 12 2016 jimmy@boombatower.com
- Update to 0.15.1 release.
* Fri Jul  8 2016 jimmy@boombatower.com
- Update to 0.15.0 release.
* Mon May 16 2016 jimmy@boombatower.com
- Update to 0.14.2 release.
* Tue Apr 26 2016 jimmy@boombatower.com
- Update to 0.14.1 release.
* Sat Apr 16 2016 olaf@aepfle.de
- Use pkgconfig instead of libffmpeg-devel
* Tue Mar 22 2016 jimmy@boombatower.com
- Update to 0.13.4 release.
* Sun Mar 20 2016 jimmy@boombatower.com
- Update to 0.13.3 release.
* Mon Feb 29 2016 jimmy@boombatower.com
- Update to 0.13.2 release.
* Fri Feb  5 2016 jimmy@boombatower.com
- Update to 0.13.1 release.
- Remove patch for gcc 4.8 compatability since it was upstreamed.
* Thu Jan 28 2016 jimmy@boombatower.com
- Update to 0.13.0 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.13.0
- Add rpmlintrc for "bad" things obs-studio requires.
- Add patch for gcc 4.8 compatability.
* Sat Dec 12 2015 jimmy@boombatower.com
- Update to 0.12.4 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.12.4
* Wed Dec  9 2015 jimmy@boombatower.com
- Change build requirement from libffmpeg-devel to ffmpeg-devel to
  follow recent linking of ffmpeg to obs version.
* Sat Dec  5 2015 jimmy@boombatower.com
- Update to 0.12.3 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.12.3
* Sat Nov 21 2015 jimmy@boombatower.com
- Update to 0.12.2 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.12.2
* Tue Nov 17 2015 jimmy@boombatower.com
- Update to 0.12.1 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.12.1
* Fri Sep 25 2015 jimmy@boombatower.com
- Update to 0.12.0 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.12.0
- Remove gcc >= 4.9 requirement since 0.12.0 reverted unintended change.
* Mon Aug 17 2015 jimmy@boombatower.com
- Update to 0.11.4 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.11.4
- Cut off git portion of version string in UI.
- Since 0.11.3 obs unofficially requires gcc 4.9 and higher which makes it
  impossible to compile on obs for openSUSE 13.2.
  https://obsproject.com/mantis/view.php?id=276
* Sun Aug  9 2015 jimmy@boombatower.com
- Update to 0.11.3 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.11.3
* Tue Jul 28 2015 jimmy@boombatower.com
- Update to 0.11.2 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.11.2
* Fri Jul 10 2015 jimmy@boombatower.com
- Update to 0.11.1 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.11.1
* Thu Jul  9 2015 jimmy@boombatower.com
- Update to 0.11.0 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.11.0
- Add curl build dependency.
* Tue May 19 2015 jimmy@boombatower.com
- Update to 0.10.1 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.10.1
* Wed May 13 2015 jimmy@boombatower.com
- Update to 0.10.0 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.10.0
* Fri Mar 27 2015 jimmy@boombatower.com
- Update to 0.9.1 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.9.1
* Thu Mar 26 2015 jimmy@boombatower.com
- Update to 0.9.0 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.9.0
* Sat Feb 21 2015 jimmy@boombatower.com
- Update to 0.8.3 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.8.3
* Thu Feb 12 2015 jimmy@boombatower.com
- Update to 0.8.2 release.
  https://github.com/jp9000/obs-studio/releases/tag/0.8.2
  https://github.com/jp9000/obs-studio/releases/tag/0.8.1
  https://github.com/jp9000/obs-studio/releases/tag/0.8.0
* Thu Jan 15 2015 jimmy@boombatower.com
- Update to 0.7.3 release.
  Details at https://github.com/jp9000/obs-studio/releases/tag/0.7.3
* Wed Jan  7 2015 jimmy@boombatower.com
- Update to 0.7.2 release.
  Details at https://github.com/jp9000/obs-studio/releases/tag/0.7.2 and
    https://github.com/jp9000/obs-studio/releases/tag/0.7.1
* Thu Nov 13 2014 jimmy@boombatower.com
- Initial 0.6.4 release.
