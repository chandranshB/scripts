#!/usr/bin/env python3

import os
import sys
import re
import threading
import time
import subprocess
import platform
from pathlib import Path
from urllib.parse import urlparse, parse_qs

def check_and_install_dependencies():
    """Check and install all required dependencies with progress tracking"""
    dependencies_to_install = []
    
    # Check Python packages
    python_packages = {
        'yt-dlp': 'yt_dlp',
        'rich': 'rich'
    }
    
    for package_name, import_name in python_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            dependencies_to_install.append(('python', package_name))
    
    # Check ffmpeg
    ffmpeg_installed = check_ffmpeg_comprehensive()
    if not ffmpeg_installed:
        dependencies_to_install.append(('ffmpeg', 'ffmpeg'))
    
    # Install dependencies with progress
    if dependencies_to_install:
        # Import rich here after we know if we need to install it
        try:
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
            from rich.console import Console
            rich_available = True
        except ImportError:
            rich_available = False
        
        print("🔧 Installing missing dependencies:")
        
        if rich_available:
            # Use Rich progress if available
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                console=Console()
            ) as progress:
                
                for dep_type, dep_name in dependencies_to_install:
                    task = progress.add_task(f"Installing {dep_name}...", total=None)
                    
                    try:
                        if dep_type == 'python':
                            install_python_package_with_progress(dep_name, progress, task)
                        elif dep_type == 'ffmpeg':
                            install_ffmpeg_robust(progress, task)
                        
                        progress.update(task, description=f"✅ {dep_name} installed")
                        # Verify installation
                        if dep_type == 'ffmpeg' and not check_ffmpeg_comprehensive():
                            progress.update(task, description=f"⚠️ {dep_name} installed but not in PATH")
                    except Exception as e:
                        progress.update(task, description=f"❌ {dep_name} failed: {str(e)[:30]}")
                        if dep_type == 'python':
                            print(f"❌ Failed to install {dep_name}: {e}")
                            sys.exit(1)
        else:
            # Fallback to simple progress without Rich
            for i, (dep_type, dep_name) in enumerate(dependencies_to_install, 1):
                print(f"   [{i}/{len(dependencies_to_install)}] Installing {dep_name}...")
                
                try:
                    if dep_type == 'python':
                        install_python_package_simple(dep_name)
                        print(f"   ✅ {dep_name} installed")
                    elif dep_type == 'ffmpeg':
                        install_ffmpeg_robust()
                        if check_ffmpeg_comprehensive():
                            print(f"   ✅ ffmpeg installed")
                        else:
                            print(f"   ⚠️ ffmpeg installed but may need PATH refresh")
                except Exception as e:
                    print(f"   ❌ {dep_name} failed: {e}")
                    if dep_type == 'python':
                        sys.exit(1)
        
        print("✅ All dependencies processed successfully!\n")

def check_ffmpeg_comprehensive():
    """Comprehensive FFmpeg check including common installation paths"""
    # Method 1: Try running ffmpeg command
    try:
        with open(os.devnull, 'w') as devnull:
            subprocess.run(['ffmpeg', '-version'], 
                          stdout=devnull, stderr=devnull, check=True, timeout=10)
            return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Method 2: Check common installation paths
    system = platform.system().lower()
    common_paths = []
    
    if system == "windows":
        common_paths = [
            Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / 'ffmpeg' / 'bin' / 'ffmpeg.exe',
            Path(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')) / 'ffmpeg' / 'bin' / 'ffmpeg.exe',
            Path.home() / 'bin' / 'ffmpeg.exe',
            Path('C:\\') / 'ffmpeg' / 'bin' / 'ffmpeg.exe',
            Path('C:\\') / 'tools' / 'ffmpeg' / 'bin' / 'ffmpeg.exe'
        ]
    elif system == "darwin":  # macOS
        common_paths = [
            Path('/opt/homebrew/bin/ffmpeg'),
            Path('/usr/local/bin/ffmpeg'),
            Path('/usr/bin/ffmpeg'),
            Path.home() / 'bin' / 'ffmpeg'
        ]
    elif system == "linux":
        common_paths = [
            Path('/usr/bin/ffmpeg'),
            Path('/usr/local/bin/ffmpeg'),
            Path('/opt/ffmpeg/bin/ffmpeg'),
            Path.home() / 'bin' / 'ffmpeg',
            Path('/snap/bin/ffmpeg')
        ]
    
    # Check if ffmpeg exists in common paths and add to PATH if found
    for ffmpeg_path in common_paths:
        if ffmpeg_path.exists():
            ffmpeg_dir = str(ffmpeg_path.parent)
            current_path = os.environ.get('PATH', '')
            if ffmpeg_dir not in current_path:
                os.environ['PATH'] = ffmpeg_dir + os.pathsep + current_path
                # Try again with updated PATH
                try:
                    with open(os.devnull, 'w') as devnull:
                        subprocess.run(['ffmpeg', '-version'], 
                                      stdout=devnull, stderr=devnull, check=True, timeout=10)
                        return True
                except:
                    continue
            return True
    
    return False

def install_python_package_with_progress(package_name, progress, task):
    """Install Python package with progress updates"""
    progress.update(task, description=f"📦 Downloading {package_name}...")
    
    # Use a separate process to install and capture output
    process = subprocess.Popen([
        sys.executable, "-m", "pip", "install", package_name, "--upgrade"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            # Update progress description based on pip output
            if 'Downloading' in output:
                progress.update(task, description=f"📥 Downloading {package_name}...")
            elif 'Installing' in output:
                progress.update(task, description=f"🔧 Installing {package_name}...")
            elif 'Successfully installed' in output:
                progress.update(task, description=f"✅ {package_name} installed")
    
    if process.returncode != 0:
        raise Exception(f"pip install failed with code {process.returncode}")

def install_python_package_simple(package_name):
    """Simple Python package installation without Rich"""
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", package_name, "--upgrade", "--quiet"
    ])

def install_ffmpeg_robust(progress=None, task=None):
    """Robust FFmpeg installation with multiple fallback methods"""
    system = platform.system().lower()
    
    def update_progress(message):
        if progress and task:
            progress.update(task, description=message)
        else:
            print(f"   {message}")
    
    try:
        if system == "windows":
            install_ffmpeg_windows_robust(update_progress)
        elif system == "darwin":  # macOS
            install_ffmpeg_macos_robust(update_progress)
        elif system == "linux":
            install_ffmpeg_linux_robust(update_progress)
        else:
            raise Exception("Unsupported operating system")
            
        # Verify installation after completion
        if check_ffmpeg_comprehensive():
            update_progress("✅ FFmpeg installed and verified")
        else:
            update_progress("⚠️ FFmpeg installed but verification failed")
            
    except Exception as e:
        update_progress(f"❌ FFmpeg installation failed: {str(e)[:30]}")
        print(f"\n⚠️ FFmpeg installation failed: {e}")
        print("The downloader will work but may have limited format support.")
        print("You can manually install FFmpeg from: https://ffmpeg.org/download.html")

def run_command_safe(cmd, shell=False, check=True, timeout=300):
    """Run command with proper error handling and timeout"""
    try:
        with open(os.devnull, 'w') as devnull:
            if shell:
                return subprocess.run(cmd, shell=True, stdout=devnull, stderr=devnull, 
                                    check=check, timeout=timeout)
            else:
                return subprocess.run(cmd, stdout=devnull, stderr=devnull, 
                                    check=check, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise Exception(f"Command timed out after {timeout} seconds")
    except subprocess.CalledProcessError as e:
        if check:
            raise e
        return e

def install_ffmpeg_windows_robust(update_progress):
    """Robust FFmpeg installation for Windows with multiple methods"""
    
    # Method 1: Try winget (Windows 10 1809+ and Windows 11)
    update_progress("🔍 Trying winget...")
    try:
        # Check if winget is available
        subprocess.run(['winget', '--version'], capture_output=True, check=True, timeout=10)
        update_progress("🚀 Installing via winget...")
        run_command_safe(['winget', 'install', '--id', 'Gyan.FFmpeg', '--silent', '--accept-source-agreements'])
        if check_ffmpeg_comprehensive():
            return
    except:
        pass
    
    # Method 2: Try chocolatey
    update_progress("🍫 Trying chocolatey...")
    try:
        subprocess.run(['choco', '--version'], capture_output=True, check=True, timeout=10)
        update_progress("🍫 Installing via chocolatey...")
        run_command_safe(['choco', 'install', 'ffmpeg', '-y'])
        if check_ffmpeg_comprehensive():
            return
    except:
        pass
    
    # Method 3: Try scoop
    update_progress("🥄 Trying scoop...")
    try:
        subprocess.run(['scoop', '--version'], capture_output=True, check=True, timeout=10)
        update_progress("🥄 Installing via scoop...")
        run_command_safe(['scoop', 'install', 'ffmpeg'])
        if check_ffmpeg_comprehensive():
            return
    except:
        pass
    
    # Method 4: Manual installation with multiple sources
    update_progress("📥 Manual installation...")
    install_ffmpeg_windows_manual_robust(update_progress)

def install_ffmpeg_windows_manual_robust(update_progress):
    """Robust manual FFmpeg installation for Windows"""
    import urllib.request
    import zipfile
    import shutil
    
    # Multiple download sources
    download_sources = [
        {
            'url': 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip',
            'name': 'Gyan.dev builds'
        },
        {
            'url': 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip',
            'name': 'BtbN GitHub builds'
        }
    ]
    
    temp_dir = Path(os.environ.get('TEMP', 'C:\\temp')) / "ffmpeg_install"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        success = False
        for source in download_sources:
            try:
                update_progress(f"📥 Downloading from {source['name']}...")
                zip_path = temp_dir / "ffmpeg.zip"
                
                # Download with timeout and retries
                for attempt in range(3):
                    try:
                        urllib.request.urlretrieve(source['url'], zip_path)
                        break
                    except Exception as e:
                        if attempt == 2:
                            raise e
                        update_progress(f"📥 Retry {attempt + 2}/3...")
                        time.sleep(2)
                
                # Extract
                update_progress("📂 Extracting files...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find ffmpeg.exe
                ffmpeg_exe = None
                for root, dirs, files in os.walk(temp_dir):
                    if 'ffmpeg.exe' in files:
                        ffmpeg_exe = Path(root) / 'ffmpeg.exe'
                        break
                
                if not ffmpeg_exe or not ffmpeg_exe.exists():
                    continue
                
                # Install to multiple locations for maximum compatibility
                update_progress("🔧 Installing FFmpeg...")
                
                install_locations = [
                    Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / 'ffmpeg' / 'bin',
                    Path('C:\\') / 'ffmpeg' / 'bin',
                    Path.home() / 'bin',
                    Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local')) / 'ffmpeg' / 'bin'
                ]
                
                installed = False
                for install_dir in install_locations:
                    try:
                        install_dir.mkdir(parents=True, exist_ok=True)
                        target_path = install_dir / 'ffmpeg.exe'
                        shutil.copy2(ffmpeg_exe, target_path)
                        
                        # Update PATH
                        update_path_windows(str(install_dir))
                        
                        # Test if it works
                        if check_ffmpeg_comprehensive():
                            installed = True
                            break
                            
                    except PermissionError:
                        continue
                    except Exception:
                        continue
                
                if installed:
                    success = True
                    break
                    
            except Exception as e:
                continue
        
        if not success:
            raise Exception("All download sources failed")
            
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

def update_path_windows(new_path):
    """Update Windows PATH environment variable"""
    current_path = os.environ.get('PATH', '')
    if new_path not in current_path:
        # Update for current session
        os.environ['PATH'] = new_path + os.pathsep + current_path
        
        # Try to update system PATH (requires admin) or user PATH
        try:
            # Try system PATH first
            run_command_safe(f'setx PATH "{new_path};%PATH%" /M', shell=True, check=False)
        except:
            try:
                # Fallback to user PATH
                run_command_safe(f'setx PATH "{new_path};%PATH%"', shell=True, check=False)
            except:
                pass

def install_ffmpeg_macos_robust(update_progress):
    """Robust FFmpeg installation for macOS"""
    
    # Method 1: Try Homebrew
    update_progress("🍺 Checking Homebrew...")
    try:
        subprocess.run(['brew', '--version'], capture_output=True, check=True, timeout=10)
        homebrew_available = True
    except:
        homebrew_available = False
    
    if not homebrew_available:
        update_progress("🍺 Installing Homebrew...")
        try:
            # Install Homebrew
            install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            subprocess.run(install_cmd, shell=True, check=True, timeout=600)
            
            # Add to PATH
            homebrew_paths = ['/opt/homebrew/bin', '/usr/local/bin']
            current_path = os.environ.get('PATH', '')
            for path in homebrew_paths:
                if Path(path).exists() and path not in current_path:
                    os.environ['PATH'] = path + os.pathsep + current_path
                    break
        except:
            pass
    
    if homebrew_available or check_command_exists('brew'):
        update_progress("🔧 Installing FFmpeg via Homebrew...")
        try:
            run_command_safe(['brew', 'install', 'ffmpeg'], timeout=600)
            if check_ffmpeg_comprehensive():
                return
        except:
            pass
    
    # Method 2: Try MacPorts
    update_progress("🚢 Trying MacPorts...")
    try:
        if check_command_exists('port'):
            run_command_safe(['sudo', 'port', 'install', 'ffmpeg'], timeout=600)
            if check_ffmpeg_comprehensive():
                return
    except:
        pass
    
    # Method 3: Manual binary installation
    update_progress("📥 Manual installation...")
    install_ffmpeg_macos_manual(update_progress)

def install_ffmpeg_macos_manual(update_progress):
    """Manual FFmpeg installation for macOS"""
    import urllib.request
    import tarfile
    import shutil
    
    update_progress("📥 Downloading FFmpeg binary...")
    temp_dir = Path("/tmp") / "ffmpeg_install"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Download static build
        ffmpeg_url = "https://evermeet.cx/ffmpeg/getrelease/zip"
        zip_path = temp_dir / "ffmpeg.zip"
        
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        
        # Extract
        update_progress("📂 Extracting...")
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Install
        update_progress("🔧 Installing...")
        ffmpeg_binary = temp_dir / "ffmpeg"
        if ffmpeg_binary.exists():
            install_locations = [
                Path("/usr/local/bin"),
                Path.home() / "bin"
            ]
            
            for install_dir in install_locations:
                try:
                    install_dir.mkdir(parents=True, exist_ok=True)
                    target = install_dir / "ffmpeg"
                    shutil.copy2(ffmpeg_binary, target)
                    os.chmod(target, 0o755)
                    
                    # Update PATH
                    current_path = os.environ.get('PATH', '')
                    if str(install_dir) not in current_path:
                        os.environ['PATH'] = str(install_dir) + os.pathsep + current_path
                    
                    if check_ffmpeg_comprehensive():
                        break
                except:
                    continue
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def install_ffmpeg_linux_robust(update_progress):
    """Robust FFmpeg installation for Linux"""
    
    # Enhanced package managers list with better commands
    package_managers = [
        # Ubuntu/Debian - try multiple methods
        ('apt', ['sudo', 'apt', 'update', '-y'], ['sudo', 'apt', 'install', '-y', 'ffmpeg']),
        ('apt-get', None, ['sudo', 'apt-get', 'install', '-y', 'ffmpeg']),
        
        # Fedora/RHEL
        ('dnf', None, ['sudo', 'dnf', 'install', '-y', 'ffmpeg', '--allowerasing']),
        ('yum', ['sudo', 'yum', 'install', '-y', 'epel-release'], ['sudo', 'yum', 'install', '-y', 'ffmpeg']),
        
        # Arch Linux
        ('pacman', None, ['sudo', 'pacman', '-S', '--noconfirm', 'ffmpeg']),
        
        # openSUSE
        ('zypper', ['sudo', 'zypper', 'refresh'], ['sudo', 'zypper', 'install', '-y', 'ffmpeg']),
        
        # Alpine
        ('apk', ['sudo', 'apk', 'update'], ['sudo', 'apk', 'add', 'ffmpeg']),
        
        # Gentoo
        ('emerge', None, ['sudo', 'emerge', 'media-video/ffmpeg']),
    ]
    
    update_progress("🔍 Detecting package manager...")
    
    for pm_name, update_cmd, install_cmd in package_managers:
        try:
            # Check if package manager exists
            if not check_command_exists(pm_name):
                continue
                
            update_progress(f"📦 Using {pm_name}...")
            
            # Update package lists if needed
            if update_cmd:
                update_progress(f"🔄 Updating package lists...")
                try:
                    run_command_safe(update_cmd, timeout=300)
                except:
                    pass  # Continue even if update fails
            
            # Install ffmpeg
            update_progress(f"🔧 Installing FFmpeg via {pm_name}...")
            run_command_safe(install_cmd, timeout=600)
            
            # Verify installation
            if check_ffmpeg_comprehensive():
                return
                
        except Exception as e:
            continue
    
    # Try universal package managers
    update_progress("📦 Trying universal package managers...")
    
    # Try snap
    try:
        if check_command_exists('snap'):
            update_progress("📦 Installing via snap...")
            run_command_safe(['sudo', 'snap', 'install', 'ffmpeg'])
            if check_ffmpeg_comprehensive():
                return
    except:
        pass
    
    # Try flatpak
    try:
        if check_command_exists('flatpak'):
            update_progress("📦 Installing via flatpak...")
            run_command_safe(['flatpak', 'install', '-y', 'flathub', 'org.freedesktop.Platform.ffmpeg-full'])
            if check_ffmpeg_comprehensive():
                return
    except:
        pass
    
    # Try AppImage or static build
    update_progress("📥 Trying static build...")
    install_ffmpeg_linux_static(update_progress)

def install_ffmpeg_linux_static(update_progress):
    """Install static FFmpeg build on Linux"""
    import urllib.request
    import tarfile
    import shutil
    
    temp_dir = Path("/tmp") / "ffmpeg_install"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Download static build
        update_progress("📥 Downloading static build...")
        ffmpeg_url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        tar_path = temp_dir / "ffmpeg-static.tar.xz"
        
        urllib.request.urlretrieve(ffmpeg_url, tar_path)
        
        # Extract
        update_progress("📂 Extracting...")
        with tarfile.open(tar_path, 'r:xz') as tar_ref:
            tar_ref.extractall(temp_dir)
        
        # Find and install ffmpeg binary
        update_progress("🔧 Installing...")
        ffmpeg_binary = None
        for root, dirs, files in os.walk(temp_dir):
            if 'ffmpeg' in files:
                candidate = Path(root) / 'ffmpeg'
                if candidate.is_file() and os.access(candidate, os.X_OK):
                    ffmpeg_binary = candidate
                    break
        
        if ffmpeg_binary:
            install_locations = [
                Path("/usr/local/bin"),
                Path.home() / "bin",
                Path("/opt/ffmpeg/bin")
            ]
            
            for install_dir in install_locations:
                try:
                    install_dir.mkdir(parents=True, exist_ok=True)
                    target = install_dir / "ffmpeg"
                    shutil.copy2(ffmpeg_binary, target)
                    os.chmod(target, 0o755)
                    
                    # Update PATH
                    current_path = os.environ.get('PATH', '')
                    if str(install_dir) not in current_path:
                        os.environ['PATH'] = str(install_dir) + os.pathsep + current_path
                    
                    if check_ffmpeg_comprehensive():
                        break
                except:
                    continue
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def check_command_exists(command):
    """Check if a command exists in PATH"""
    try:
        subprocess.run([command, '--version'], capture_output=True, check=True, timeout=10)
        return True
    except:
        try:
            subprocess.run(['which', command], capture_output=True, check=True, timeout=10)
            return True
        except:
            return False

# Install dependencies before importing other modules
check_and_install_dependencies()

# Now import the modules (they should be installed)
import yt_dlp
from rich.console import Console
from rich.progress import (
    Progress, TextColumn, BarColumn, TaskProgressColumn, 
    TimeRemainingColumn, DownloadColumn, TransferSpeedColumn,
    SpinnerColumn
)
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.status import Status

console = Console()

class ProgressTracker:
    """Clean progress tracker with real-time updates"""
    
    def __init__(self, progress_obj, task_id):
        self.progress_obj = progress_obj
        self.task_id = task_id
        self.last_downloaded = 0
        
    def __call__(self, d):
        """Progress hook called by yt-dlp"""
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            
            if total:
                self.progress_obj.update(
                    self.task_id,
                    total=total,
                    completed=downloaded
                )
            elif downloaded > self.last_downloaded:
                # For streams without known size
                self.progress_obj.update(
                    self.task_id,
                    completed=downloaded
                )
                self.last_downloaded = downloaded
                
        elif d['status'] == 'finished':
            # Mark as complete
            total = d.get('total_bytes', 100)
            self.progress_obj.update(
                self.task_id,
                completed=total,
                total=total
            )

class RobustYTDownloader:
    def __init__(self):
        self.base_dir = Path("Downloads")
        self.base_dir.mkdir(exist_ok=True)
        
    def sanitize_filename(self, filename):
        """Sanitize filename for cross-platform compatibility"""
        return re.sub(r'[<>:"/\\|?*]', '_', filename).strip()
    
    def get_quality_formats(self):
        """Available quality options"""
        return {
            'best': 'Best available quality',
            '2160': '4K (2160p)',
            '1440': '2K (1440p)', 
            '1080': 'Full HD (1080p)',
            '720': 'HD (720p)',
            '480': 'SD (480p)',
            '360': 'Low (360p)'
        }
    
    def get_robust_format_selector(self, quality, audio_only=False):
        """Get format selector with ffmpeg support for best quality"""
        
        if audio_only:
            return 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio'
        
        # Check if ffmpeg is available for merging
        ffmpeg_available = check_ffmpeg_comprehensive()
        
        if quality == 'best':
            if ffmpeg_available:
                # With ffmpeg: can merge separate video+audio for best quality
                return (
                    'bestvideo[ext=mp4][height>=1080]+bestaudio[ext=m4a]/bestvideo[ext=mp4][height>=1080]+bestaudio/'
                    'bestvideo[ext=mp4][height>=720]+bestaudio[ext=m4a]/bestvideo[ext=mp4][height>=720]+bestaudio/'
                    'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/'
                    'best[ext=mp4][height>=1080]/best[ext=mp4][height>=720]/best[ext=mp4]/best'
                )
            else:
                # Without ffmpeg: single file formats only
                return (
                    'best[ext=mp4][vcodec^=avc1][acodec^=mp4a][height>=1080]/'
                    'best[ext=mp4][vcodec^=avc1][acodec^=mp4a][height>=720]/'
                    'best[ext=mp4][vcodec^=avc1][acodec^=mp4a]/'
                    'best[ext=mp4][height>=1080]/best[ext=mp4][height>=720]/best[ext=mp4]/'
                    'best'
                )
        else:
            # Quality-specific selection
            height = int(quality)
            if ffmpeg_available:
                # With ffmpeg: try merging for exact quality
                return (
                    f'bestvideo[height={height}][ext=mp4]+bestaudio[ext=m4a]/'
                    f'bestvideo[height={height}]+bestaudio/'
                    f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/'
                    f'bestvideo[height<={height}]+bestaudio/'
                    f'best[height={height}]/best[height<={height}]/best'
                )
            else:
                # Without ffmpeg: single file formats
                return (
                    f'best[ext=mp4][vcodec^=avc1][acodec^=mp4a][height={height}]/'
                    f'best[ext=mp4][height={height}]/'
                    f'best[ext=mp4][vcodec^=avc1][acodec^=mp4a][height<={height}]/'
                    f'best[ext=mp4][height<={height}]/'
                    f'best[height={height}]/best[height<={height}]/best'
                )
    
    def setup_ydl_options(self, output_path, quality='best', audio_only=False, 
                         embed_metadata=True, playlist_index=None):
        """Setup yt-dlp options with maximum reliability"""
        
        # Filename template
        if playlist_index is not None:
            if isinstance(playlist_index, tuple):
                index, total = playlist_index
                if total >= 100:
                    prefix = f"{index:03d} - "
                elif total >= 10:
                    prefix = f"{index:02d} - "
                else:
                    prefix = f"{index} - "
            else:
                prefix = f"{playlist_index} - "
            outtmpl = str(output_path / f'{prefix}%(title)s.%(ext)s')
        else:
            outtmpl = str(output_path / '%(title)s.%(ext)s')
        
        # Get robust format selector
        format_selector = self.get_robust_format_selector(quality, audio_only)
        
        return {
            'format': format_selector,
            'outtmpl': outtmpl,
            
            # Enable merging if ffmpeg is available
            'merge_output_format': 'mp4' if not audio_only and check_ffmpeg_comprehensive() else None,
            'addmetadata': embed_metadata,
            'embedsubs': False,
            
            # Network and reliability
            'retries': 5,
            'fragment_retries': 5,
            'socket_timeout': 30,
            'http_chunk_size': 1048576,  # 1MB chunks
            
            # Output control - COMPLETE SILENCE
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'no_color': True,
            'extract_flat': False,
            
            # Disable all extra files
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writethumbnail': False,
            'writedescrption': False,
            'writeannotations': False,
            
            # Progress tracking
            'progress_hooks': [],
        }
    
    def get_video_info(self, url):
        """Get video info silently"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            # Suppress ALL output including stderr
            with open(os.devnull, 'w') as devnull:
                old_stderr = sys.stderr
                old_stdout = sys.stdout
                sys.stderr = devnull
                sys.stdout = devnull
                
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                    return info
                finally:
                    sys.stderr = old_stderr
                    sys.stdout = old_stdout
                    
        except Exception as e:
            console.print(f"[yellow]Warning: Could not get video info - {str(e)[:50]}[/yellow]")
            return None
    
    def download_single(self, url, output_dir, video_title=None, **options):
        """Download single video with clean progress display"""
        
        # Get video info if needed
        if not video_title:
            with Status("[yellow]Getting video info...", console=console):
                info = self.get_video_info(url)
                if info:
                    video_title = self.sanitize_filename(info.get('title', 'Unknown'))
                    
                    # Show what quality we're targeting and ffmpeg status
                    quality = options.get('quality', 'best')
                    if not options.get('audio_only', False) and quality != 'best':
                        ffmpeg_status = "✅" if check_ffmpeg_comprehensive() else "⚠️"
                        console.print(f"[dim]Requesting: {quality}p quality {ffmpeg_status}[/dim]")
                else:
                    video_title = "Unknown Video"
        
        # Setup clean progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
            refresh_per_second=4,
        ) as progress:
            
            task = progress.add_task(
                f"[cyan]{video_title[:40]}{'...' if len(video_title) > 40 else ''}[/cyan]",
                total=None
            )
            
            # Setup yt-dlp options
            ydl_opts = self.setup_ydl_options(output_dir, **options)
            
            # Create progress tracker
            tracker = ProgressTracker(progress, task)
            ydl_opts['progress_hooks'] = [tracker]
            
            try:
                progress.update(task, description=f"[yellow]⚡ Starting: {video_title[:35]}{'...' if len(video_title) > 35 else ''}[/yellow]")
                
                # Download with COMPLETE output suppression
                with open(os.devnull, 'w') as devnull:
                    old_stderr = sys.stderr
                    old_stdout = sys.stdout
                    sys.stderr = devnull
                    sys.stdout = devnull
                    
                    try:
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([url])
                    finally:
                        sys.stderr = old_stderr
                        sys.stdout = old_stdout
                
                # Success
                progress.update(
                    task,
                    description=f"[green]✅ {video_title[:35]}{'...' if len(video_title) > 35 else ''}[/green]"
                )
                
                console.print(f"[green]✅ Downloaded: {video_title}[/green]")
                return True
                
            except Exception as e:
                progress.update(
                    task,
                    description=f"[red]❌ Failed: {str(e)[:30]}...[/red]"
                )
                console.print(f"[red]❌ {video_title}: {str(e)[:60]}[/red]")
                return False
    
    def download_playlist_sequential(self, urls, names, output_dir, **options):
        """Download playlist videos sequentially"""
        successful = 0
        total_videos = len(urls)
        
        console.print(f"\n[bold cyan]📥 Starting download of {total_videos} videos...[/bold cyan]")
        
        for i, (url, name) in enumerate(zip(urls, names), 1):
            console.print(f"\n[bold yellow]📺 Video {i}/{total_videos}[/bold yellow]")
            
            playlist_index = (i, total_videos) if total_videos > 1 else None
            
            if self.download_single(
                url, output_dir,
                video_title=name,
                playlist_index=playlist_index,
                **options
            ):
                successful += 1
            
            console.print(f"[dim]Progress: {i}/{total_videos} processed, {successful} successful[/dim]")
            
            if i < total_videos:
                console.print("")
        
        return successful
    
    def get_playlist_info(self, url):
        """Get playlist info silently"""
        try:
            with Status("[yellow]Loading playlist...", console=console):
                ydl_opts = {
                    'quiet': True,
                    'extract_flat': True,
                    'no_warnings': True,
                }
                
                with open(os.devnull, 'w') as devnull:
                    old_stderr = sys.stderr
                    old_stdout = sys.stdout
                    sys.stderr = devnull
                    sys.stdout = devnull
                    
                    try:
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            return ydl.extract_info(url, download=False)
                    finally:
                        sys.stderr = old_stderr
                        sys.stdout = old_stdout
                        
        except Exception as e:
            console.print(f"[red]Error loading playlist: {e}[/red]")
            return None
    
    def parse_selection(self, selection, max_count):
        """Parse video selection string"""
        if not selection or selection.lower() == 'all':
            return list(range(1, max_count + 1))
        
        indices = set()
        try:
            for part in selection.split(','):
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-', 1))
                    if start < 1 or end > max_count or start > end:
                        raise ValueError(f"Invalid range: {part}")
                    indices.update(range(start, end + 1))
                else:
                    num = int(part)
                    if num < 1 or num > max_count:
                        raise ValueError(f"Invalid number: {num}")
                    indices.add(num)
            
            return sorted(indices)
        except Exception as e:
            console.print(f"[red]Selection error: {e}[/red]")
            return None

def main():
    console.print(Panel("🎬 Chandu's YouTube Downloader", style="bold blue"))
    console.print("[dim]Automatically installs all dependencies and provides maximum quality![/dim]\n")
    
    downloader = RobustYTDownloader()
    
    # Show system status
    ffmpeg_status = "✅ Available" if check_ffmpeg_comprehensive() else "❌ Not found"
    console.print(f"[dim]FFmpeg: {ffmpeg_status}[/dim]")
    
    while True:
        console.print("\n[bold]What do you want to download?[/bold]")
        console.print("1. 🎥 Video  2. 🎵 Audio  3. 📋 Playlist  4. 🎼 Playlist Audio  5. Exit")
        
        choice = Prompt.ask("Choose", choices=["1", "2", "3", "4", "5"])
        
        if choice == "5":
            break
        
        url = Prompt.ask("🔗 YouTube URL").strip()
        if not ("youtube.com" in url or "youtu.be" in url):
            console.print("[red]Invalid YouTube URL[/red]")
            continue
        
        audio_only = choice in ['2', '4']
        is_playlist = choice in ['3', '4']
        
        # Quality selection for video
        if not audio_only:
            console.print("\n[bold cyan]Quality Options:[/bold cyan]")
            formats = downloader.get_quality_formats()
            for key, desc in formats.items():
                console.print(f"  {key}: {desc}")
            
            quality = Prompt.ask(
                "Quality",
                choices=list(formats.keys()),
                default="best"
            )
        else:
            quality = 'best'
        
        embed_metadata = Confirm.ask("Add metadata to file?", default=True)
        
        if is_playlist:
            info = downloader.get_playlist_info(url)
            if not info:
                continue
            
            entries = [e for e in info.get('entries', []) if e]
            playlist_title = info.get('title', 'Unknown Playlist')
            
            console.print(f"\n[yellow]📋 {playlist_title} ({len(entries)} videos)[/yellow]")
            
            # Show preview
            for i, entry in enumerate(entries[:5], 1):
                title = entry.get('title', 'Unknown')[:60]
                console.print(f"  {i}. {title}")
            
            if len(entries) > 5:
                console.print(f"  ... and {len(entries)-5} more videos")
            
            selection = Prompt.ask(
                f"Which videos? (1-{len(entries)}, ranges like 1-5,7)",
                default="all"
            )
            indices = downloader.parse_selection(selection, len(entries))
            
            if not indices:
                continue
            
            console.print(f"[green]✅ Selected: {len(indices)} videos[/green]")
            
            # Prepare download
            selected_entries = [entries[i-1] for i in indices]
            urls = [f"https://www.youtube.com/watch?v={e['id']}" for e in selected_entries]
            names = [e.get('title', 'Unknown') for e in selected_entries]
            
            playlist_name = downloader.sanitize_filename(playlist_title)
            output_dir = downloader.base_dir / "Playlists" / playlist_name
            output_dir.mkdir(parents=True, exist_ok=True)
            
            console.print(f"[yellow]📁 Downloading to: {output_dir}[/yellow]")
            
            successful = downloader.download_playlist_sequential(
                urls, names, output_dir,
                quality=quality,
                audio_only=audio_only,
                embed_metadata=embed_metadata
            )
            
            console.print(f"\n[green]🎉 Completed! {successful}/{len(urls)} downloads successful[/green]")
        
        else:
            # Single video
            folder_name = "Audio" if audio_only else "Videos"
            output_dir = downloader.base_dir / folder_name
            output_dir.mkdir(exist_ok=True)
            
            console.print(f"[yellow]📁 Downloading to: {output_dir}[/yellow]")
            
            result = downloader.download_single(
                url, output_dir,
                quality=quality,
                audio_only=audio_only,
                embed_metadata=embed_metadata
            )
            
            if result:
                console.print("[green]🎉 Download completed successfully![/green]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
