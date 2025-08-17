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
    ffmpeg_installed = False
    try:
        with open(os.devnull, 'w') as devnull:
            subprocess.run(['ffmpeg', '-version'], 
                          stdout=devnull, stderr=devnull, check=True)
            ffmpeg_installed = True
    except (subprocess.CalledProcessError, FileNotFoundError):
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
                            install_ffmpeg_with_progress(progress, task)
                        
                        progress.update(task, description=f"✅ {dep_name} installed")
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
                        install_ffmpeg_simple()
                        print(f"   ✅ ffmpeg installed")
                except Exception as e:
                    print(f"   ❌ {dep_name} failed: {e}")
                    if dep_type == 'python':
                        sys.exit(1)
        
        print("✅ All dependencies processed successfully!\n")

def install_python_package_with_progress(package_name, progress, task):
    """Install Python package with progress updates"""
    progress.update(task, description=f"📦 Downloading {package_name}...")
    
    # Use a separate process to install and capture output
    process = subprocess.Popen([
        sys.executable, "-m", "pip", "install", package_name
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
        sys.executable, "-m", "pip", "install", package_name, "--quiet"
    ])

def install_ffmpeg_with_progress(progress, task):
    """Install ffmpeg with progress updates"""
    system = platform.system().lower()
    
    if system == "windows":
        install_ffmpeg_windows_with_progress(progress, task)
    elif system == "darwin":  # macOS
        install_ffmpeg_macos_with_progress(progress, task)
    elif system == "linux":
        install_ffmpeg_linux_with_progress(progress, task)
    else:
        raise Exception("Unsupported operating system")

def install_ffmpeg_simple():
    """Simple ffmpeg installation without Rich"""
    system = platform.system().lower()
    
    if system == "windows":
        install_ffmpeg_windows()
    elif system == "darwin":
        install_ffmpeg_macos()
    elif system == "linux":
        install_ffmpeg_linux()
    else:
        raise Exception("Unsupported operating system")

def run_command(cmd, shell=False, check=True):
    """Run command with proper output suppression for all Python versions"""
    try:
        with open(os.devnull, 'w') as devnull:
            if shell:
                return subprocess.run(cmd, shell=True, stdout=devnull, stderr=devnull, check=check)
            else:
                return subprocess.run(cmd, stdout=devnull, stderr=devnull, check=check)
    except subprocess.CalledProcessError as e:
        if check:
            raise e
        return e

def install_ffmpeg():
    """Install ffmpeg based on the operating system with full automation"""
    system = platform.system().lower()
    
    try:
        if system == "windows":
            install_ffmpeg_windows()
        elif system == "darwin":  # macOS
            install_ffmpeg_macos()
        elif system == "linux":
            install_ffmpeg_linux()
        else:
            print("❌ Unsupported operating system for automatic ffmpeg installation")
            print("Please install ffmpeg manually from: https://ffmpeg.org/download.html")
            return False
        return True
    except Exception as e:
        print(f"❌ Failed to install ffmpeg: {e}")
        print("Continuing without ffmpeg (will use single-file formats)...")
        return False

def install_ffmpeg_windows_with_progress(progress, task):
    """Install ffmpeg on Windows with progress updates"""
    progress.update(task, description="🔍 Checking Windows package managers...")
    
    # Try winget first (Windows 10+)
    try:
        progress.update(task, description="🚀 Installing via winget...")
        run_command(['winget', 'install', '--id', 'Gyan.FFmpeg', '--silent'])
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try chocolatey
    try:
        progress.update(task, description="🍫 Installing via chocolatey...")
        run_command(['choco', 'install', 'ffmpeg', '-y'])
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try scoop
    try:
        progress.update(task, description="🥄 Installing via scoop...")
        run_command(['scoop', 'install', 'ffmpeg'])
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Manual download and install
    progress.update(task, description="📥 Downloading ffmpeg manually...")
    install_ffmpeg_windows_manual_with_progress(progress, task)

def install_ffmpeg_windows_manual_with_progress(progress, task):
    """Manually install ffmpeg on Windows with progress"""
    import urllib.request
    import zipfile
    import shutil
    
    # Create temp directory
    temp_dir = Path(os.environ.get('TEMP', 'C:\\temp')) / "ffmpeg_install"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Download with progress
        progress.update(task, description="📥 Downloading ffmpeg archive...")
        ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = temp_dir / "ffmpeg.zip"
        
        def download_progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                progress.update(task, description=f"📥 Downloading ffmpeg... {percent}%")
        
        urllib.request.urlretrieve(ffmpeg_url, zip_path, download_progress_hook)
        
        # Extract
        progress.update(task, description="📂 Extracting files...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find and install ffmpeg.exe
        progress.update(task, description="🔧 Installing ffmpeg...")
        ffmpeg_exe = None
        for root, dirs, files in os.walk(temp_dir):
            if 'ffmpeg.exe' in files:
                ffmpeg_exe = Path(root) / 'ffmpeg.exe'
                break
        
        if ffmpeg_exe and ffmpeg_exe.exists():
            try:
                # Try Program Files first
                program_files = Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files'))
                ffmpeg_dir = program_files / "ffmpeg" / "bin"
                ffmpeg_dir.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(ffmpeg_exe, ffmpeg_dir / "ffmpeg.exe")
                
                # Update PATH
                current_path = os.environ.get('PATH', '')
                if str(ffmpeg_dir) not in current_path:
                    run_command(f'setx PATH "{current_path};{ffmpeg_dir}"', shell=True, check=False)
                os.environ['PATH'] = str(ffmpeg_dir) + os.pathsep + current_path
                
            except PermissionError:
                # Fallback to user directory
                user_bin = Path.home() / "bin"
                user_bin.mkdir(exist_ok=True)
                shutil.copy2(ffmpeg_exe, user_bin / "ffmpeg.exe")
                
                current_path = os.environ.get('PATH', '')
                os.environ['PATH'] = str(user_bin) + os.pathsep + current_path
        else:
            raise Exception("Could not find ffmpeg.exe in archive")
            
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

def install_ffmpeg_macos_with_progress(progress, task):
    """Install ffmpeg on macOS with progress updates"""
    # Check if Homebrew is installed
    try:
        run_command(['brew', '--version'])
        homebrew_installed = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        homebrew_installed = False
    
    if not homebrew_installed:
        progress.update(task, description="🍺 Installing Homebrew first...")
        install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        os.system(install_cmd)
        
        # Add to PATH
        homebrew_paths = ['/opt/homebrew/bin', '/usr/local/bin']
        current_path = os.environ.get('PATH', '')
        for path in homebrew_paths:
            if Path(path).exists() and path not in current_path:
                os.environ['PATH'] = path + os.pathsep + current_path
                break
    
    # Install ffmpeg
    progress.update(task, description="🔧 Installing ffmpeg via Homebrew...")
    
    # Run brew install with live output capture
    process = subprocess.Popen(['brew', 'install', 'ffmpeg'], 
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                              text=True, bufsize=1)
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            if 'Downloading' in output:
                progress.update(task, description="📥 Downloading ffmpeg...")
            elif 'Installing' in output:
                progress.update(task, description="🔧 Installing ffmpeg...")
            elif 'Pouring' in output:
                progress.update(task, description="🍺 Finalizing installation...")

def install_ffmpeg_linux_with_progress(progress, task):
    """Install ffmpeg on Linux with progress updates"""
    progress.update(task, description="🔍 Detecting package manager...")
    
    # Package managers with progress-friendly commands
    package_managers = [
        # Ubuntu/Debian
        ('apt', ['sudo', 'apt', 'update'], ['sudo', 'apt', 'install', '-y', 'ffmpeg']),
        # Fedora
        ('dnf', None, ['sudo', 'dnf', 'install', '-y', 'ffmpeg']),
        # RHEL/CentOS
        ('yum', ['sudo', 'yum', 'install', '-y', 'epel-release'], ['sudo', 'yum', 'install', '-y', 'ffmpeg']),
        # Arch Linux
        ('pacman', None, ['sudo', 'pacman', '-S', '--noconfirm', 'ffmpeg']),
        # openSUSE
        ('zypper', None, ['sudo', 'zypper', 'install', '-y', 'ffmpeg']),
        # Alpine
        ('apk', None, ['sudo', 'apk', 'add', 'ffmpeg']),
    ]
    
    for pm_name, update_cmd, install_cmd in package_managers:
        try:
            # Check if package manager exists
            run_command(['which', pm_name])
            
            progress.update(task, description=f"📦 Using {pm_name} package manager...")
            
            if update_cmd:
                progress.update(task, description=f"🔄 Updating package lists...")
                run_command(update_cmd)
            
            progress.update(task, description=f"🔧 Installing ffmpeg via {pm_name}...")
            
            # Run install command with progress monitoring
            process = subprocess.Popen(install_cmd, stdout=subprocess.PIPE, 
                                     stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    if any(word in output.lower() for word in ['downloading', 'download']):
                        progress.update(task, description=f"📥 Downloading ffmpeg...")
                    elif any(word in output.lower() for word in ['installing', 'install']):
                        progress.update(task, description=f"🔧 Installing ffmpeg...")
                    elif any(word in output.lower() for word in ['configuring', 'setting up']):
                        progress.update(task, description=f"⚙️ Configuring ffmpeg...")
            
            if process.returncode == 0:
                return
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    # Try snap as fallback
    try:
        progress.update(task, description="📦 Trying snap installation...")
        run_command(['sudo', 'snap', 'install', 'ffmpeg'])
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try flatpak as last resort
    try:
        progress.update(task, description="📦 Trying flatpak installation...")
        run_command(['flatpak', 'install', '-y', 'flathub', 'org.freedesktop.Platform.ffmpeg-full'])
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    raise Exception("No supported package manager found")

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
        ffmpeg_available = self.check_ffmpeg()
        
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
    
    def check_ffmpeg(self):
        """Check if ffmpeg is available"""
        try:
            with open(os.devnull, 'w') as devnull:
                subprocess.run(['ffmpeg', '-version'], 
                              stdout=devnull, stderr=devnull, check=True)
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
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
            'merge_output_format': 'mp4' if not audio_only and self.check_ffmpeg() else None,
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
                        ffmpeg_status = "✅" if self.check_ffmpeg() else "⚠️"
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
    ffmpeg_status = "✅ Available" if downloader.check_ffmpeg() else "❌ Not found"
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
