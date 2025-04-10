# PURPOSE: RAID 설정 및 관리를 위한 주요 기능을 포함하는 모듈
"""
RAID 설정, 해제, 상태 확인 등의 주요 기능을 제공하는 모듈
"""

import os
import subprocess
from typing import List, Optional
from rich.console import Console
from rich.prompt import Confirm, Prompt
from .utils import run_command, get_disk_list, display_disk_table

console = Console()

class RAIDManager:
    def __init__(self):
        self.console = Console()
    
    def setup_raid(self, disks: List[str], level: int, device_name: str, mount_point: str) -> bool:
        """RAID 배열을 설정합니다."""
        try:
            # 디스크 선택 확인
            self.console.print("\n[red]경고: 선택한 디스크의 모든 데이터가 삭제됩니다![/red]")
            if not Confirm.ask("계속하시겠습니까?"):
                return False
            
            # 디스크 상태 확인
            for disk in disks:
                if not self._check_disk_health(disk):
                    if not Confirm.ask(f"[yellow]경고: {disk}의 상태가 좋지 않습니다. 계속하시겠습니까?[/yellow]"):
                        return False
            
            # RAID 레벨별 최소 디스크 수 확인
            min_disks = {
                0: 2,  # RAID 0
                1: 2,  # RAID 1
                5: 3,  # RAID 5
                6: 4   # RAID 6
            }
            
            if len(disks) < min_disks[level]:
                self.console.print(f"[red]오류: RAID {level}은 최소 {min_disks[level]}개의 디스크가 필요합니다.[/red]")
                return False
            
            # 디스크 용량 확인
            if not self._check_disk_sizes(disks):
                if not Confirm.ask("[yellow]경고: 선택한 디스크들의 용량이 다릅니다. 계속하시겠습니까?[/yellow]"):
                    return False
            
            # 파티션 생성
            for disk in disks:
                self._create_partition(disk)
            
            # RAID 배열 생성
            self._create_raid_array(disks, level, device_name)
            
            # 파일 시스템 생성
            self._create_filesystem(device_name)
            
            # 마운트 포인트 생성 및 마운트
            self._mount_raid(device_name, mount_point)
            
            # fstab 설정
            self._update_fstab(device_name, mount_point)
            
            # 시스템 업데이트
            self._update_system()
            
            self.console.print("[green]RAID 설정이 완료되었습니다![/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]RAID 설정 중 오류 발생: {str(e)}[/red]")
            return False
    
    def _create_partition(self, disk: str) -> None:
        """디스크에 파티션을 생성합니다."""
        # GPT 레이블 생성
        run_command(["parted", "-s", disk, "mklabel", "gpt"])
        
        # 파티션 생성
        run_command(["parted", "-s", disk, "mkpart", "primary", "0%", "100%"])
        
        # RAID 플래그 설정
        run_command(["parted", "-s", disk, "set", "1", "raid", "on"])
    
    def _create_raid_array(self, disks: List[str], level: int, device_name: str) -> None:
        """RAID 배열을 생성합니다."""
        partitions = [f"{disk}1" for disk in disks]
        cmd = [
            "mdadm", "--create", "--verbose",
            device_name,
            "--level", str(level),
            "--raid-devices", str(len(disks))
        ] + partitions
        
        run_command(cmd)
    
    def _create_filesystem(self, device_name: str) -> None:
        """RAID 배열에 파일 시스템을 생성합니다."""
        run_command(["mkfs.ext4", device_name])
    
    def _mount_raid(self, device_name: str, mount_point: str) -> None:
        """RAID를 마운트합니다."""
        os.makedirs(mount_point, exist_ok=True)
        run_command(["mount", device_name, mount_point])
    
    def _update_fstab(self, device_name: str, mount_point: str) -> None:
        """fstab에 RAID 마운트 설정을 추가합니다."""
        try:
            # UUID 가져오기
            result = run_command(["blkid", "-s", "UUID", "-o", "value", device_name])
            uuid = result.stdout.strip()
            
            # RAID 레벨 확인
            raid_level = self._get_raid_level(device_name)
            
            # 기본 마운트 옵션 설정
            mount_options = "defaults"
            
            # RAID 레벨에 따른 추가 옵션
            if raid_level in [1, 5, 6]:  # RAID 1, 5, 6의 경우
                mount_options += ",nofail,x-systemd.device-timeout=5"
            else:  # RAID 0의 경우
                mount_options += ",nofail,x-systemd.device-timeout=3"
            
            # fstab에 추가
            fstab_entry = f"UUID={uuid} {mount_point} ext4 {mount_options} 0 0\n"
            
            # fstab 백업
            backup_file = "/etc/fstab.backup"
            run_command(["cp", "/etc/fstab", backup_file])
            
            # fstab에 추가
            with open("/etc/fstab", "a") as f:
                f.write(fstab_entry)
            
            self.console.print("[green]fstab 설정이 업데이트되었습니다.[/green]")
            self.console.print(f"[yellow]백업 파일: {backup_file}[/yellow]")
            
        except Exception as e:
            self.console.print(f"[red]fstab 설정 중 오류 발생: {str(e)}[/red]")
            raise
    
    def _get_raid_level(self, device_name: str) -> int:
        """RAID 디바이스의 레벨을 반환합니다."""
        try:
            result = run_command(["mdadm", "--detail", device_name])
            for line in result.stdout.split("\n"):
                if "Raid Level" in line:
                    level = line.split(":")[1].strip().lower()
                    if "raid0" in level:
                        return 0
                    elif "raid1" in level:
                        return 1
                    elif "raid5" in level:
                        return 5
                    elif "raid6" in level:
                        return 6
            return 0  # 기본값
        except Exception:
            return 0  # 오류 시 기본값
    
    def _update_system(self) -> None:
        """시스템 설정을 업데이트합니다."""
        # mdadm.conf 업데이트
        run_command(["mdadm", "--detail", "--scan"], stdout=open("/etc/mdadm/mdadm.conf", "w"))
        
        # initramfs 업데이트
        run_command(["update-initramfs", "-u"])
    
    def remove_raid(self, device_name: str) -> bool:
        """RAID 배열을 제거합니다."""
        try:
            # RAID 배열 중지
            run_command(["mdadm", "--stop", device_name])
            
            # 슈퍼블록 제거
            for disk in self._get_raid_disks(device_name):
                run_command(["mdadm", "--zero-superblock", disk])
            
            # fstab에서 제거
            self._remove_from_fstab(device_name)
            
            self.console.print("[green]RAID 배열이 제거되었습니다![/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]RAID 제거 중 오류 발생: {str(e)}[/red]")
            return False
    
    def _get_raid_disks(self, device_name: str) -> List[str]:
        """RAID 배열의 디스크 목록을 반환합니다."""
        result = run_command(["mdadm", "--detail", device_name])
        disks = []
        for line in result.stdout.split("\n"):
            if line.startswith("    "):
                parts = line.strip().split()
                if len(parts) >= 7 and parts[0].startswith("/dev/"):
                    disks.append(parts[0])
        return disks
    
    def _remove_from_fstab(self, device_name: str) -> None:
        """fstab에서 RAID 설정을 제거합니다."""
        result = run_command(["blkid", "-s", "UUID", "-o", "value", device_name])
        uuid = result.stdout.strip()
        
        with open("/etc/fstab", "r") as f:
            lines = f.readlines()
        
        with open("/etc/fstab", "w") as f:
            for line in lines:
                if uuid not in line:
                    f.write(line)
    
    def change_mount_point(self, device_name: str, new_mount_point: str) -> bool:
        """RAID의 마운트 포인트를 변경합니다."""
        try:
            # 현재 마운트 해제
            run_command(["umount", device_name])
            
            # 새 마운트 포인트 생성
            os.makedirs(new_mount_point, exist_ok=True)
            
            # 새 위치에 마운트
            run_command(["mount", device_name, new_mount_point])
            
            # fstab 업데이트
            self._update_fstab(device_name, new_mount_point)
            
            self.console.print("[green]마운트 포인트가 변경되었습니다![/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]마운트 포인트 변경 중 오류 발생: {str(e)}[/red]")
            return False
    
    def _check_disk_health(self, disk: str) -> bool:
        """디스크의 건강 상태를 확인합니다."""
        try:
            result = run_command(["smartctl", "-H", disk])
            return "PASSED" in result.stdout
        except Exception:
            return True  # smartctl이 실패하면 기본적으로 True 반환
    
    def _check_disk_sizes(self, disks: List[str]) -> bool:
        """디스크들의 용량이 동일한지 확인합니다."""
        try:
            sizes = []
            for disk in disks:
                result = run_command(["blockdev", "--getsize64", disk])
                sizes.append(int(result.stdout.strip()))
            
            return len(set(sizes)) == 1
        except Exception:
            return False
    
    def recommend_raid_level(self, num_disks: int, disk_sizes: List[int]) -> int:
        """디스크 수와 용량을 기반으로 RAID 레벨을 추천합니다."""
        if num_disks == 2:
            return 1  # RAID 1 추천 (미러링)
        elif num_disks == 3:
            return 5  # RAID 5 추천 (패리티)
        elif num_disks >= 4:
            if min(disk_sizes) == max(disk_sizes):
                return 6  # RAID 6 추천 (이중 패리티)
            else:
                return 5  # RAID 5 추천 (패리티)
        else:
            return 0  # RAID 0 추천 (스트라이핑)
    
    def get_raid_level_description(self, level: int) -> str:
        """RAID 레벨에 대한 설명을 반환합니다."""
        descriptions = {
            0: "스트라이핑 - 최대 성능, 데이터 중복 없음",
            1: "미러링 - 최대 안정성, 50% 용량 효율",
            5: "패리티 - 성능과 안정성의 균형, 1개 디스크 장애 허용",
            6: "이중 패리티 - 최대 안정성, 2개 디스크 장애 허용"
        }
        return descriptions.get(level, "알 수 없는 RAID 레벨")
    
    def remount_device(self, device_name: str) -> bool:
        """디바이스를 재마운트합니다."""
        try:
            # 현재 마운트 정보 확인
            mount_info = self._get_mount_info(device_name)
            if not mount_info:
                self.console.print(f"[red]오류: {device_name}의 마운트 정보를 찾을 수 없습니다.[/red]")
                return False
            
            # RAID 디바이스인지 확인
            is_raid = device_name.startswith('/dev/md')
            
            # 현재 마운트 해제
            self.console.print(f"[yellow]{device_name} 언마운트 중...[/yellow]")
            run_command(["umount", device_name])
            
            # RAID 디바이스인 경우 RAID 상태 확인
            if is_raid:
                self.console.print("[yellow]RAID 상태 확인 중...[/yellow]")
                raid_status = self._check_raid_status(device_name)
                if not raid_status['healthy']:
                    self.console.print(f"[red]경고: RAID 상태가 비정상입니다: {raid_status['message']}[/red]")
                    if not Confirm.ask("계속 진행하시겠습니까?"):
                        return False
            
            # fstab 설정 업데이트
            self.console.print("[yellow]fstab 설정 업데이트 중...[/yellow]")
            self._update_fstab(device_name, mount_info['mountpoint'])
            
            # 재마운트
            self.console.print(f"[yellow]{device_name} 재마운트 중...[/yellow]")
            if is_raid:
                # RAID 디바이스는 mount -a 대신 직접 마운트
                run_command(["mount", device_name, mount_info['mountpoint']])
            else:
                run_command(["mount", "-a"])
            
            self.console.print("[green]재마운트가 완료되었습니다![/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]재마운트 중 오류 발생: {str(e)}[/red]")
            return False
    
    def _check_raid_status(self, device_name: str) -> dict:
        """RAID 디바이스의 상태를 확인합니다."""
        try:
            result = run_command(["mdadm", "--detail", device_name])
            status = {
                'healthy': True,
                'message': '정상'
            }
            
            for line in result.stdout.split("\n"):
                if "State" in line:
                    state = line.split(":")[1].strip()
                    if "clean" not in state.lower():
                        status['healthy'] = False
                        status['message'] = f"RAID 상태: {state}"
                elif "Failed Devices" in line:
                    failed = int(line.split(":")[1].strip())
                    if failed > 0:
                        status['healthy'] = False
                        status['message'] = f"실패한 디스크: {failed}개"
            
            return status
        except Exception as e:
            return {
                'healthy': False,
                'message': f"상태 확인 실패: {str(e)}"
            }
    
    def _get_mount_info(self, device_name: str) -> Optional[dict]:
        """디바이스의 마운트 정보를 반환합니다."""
        try:
            # mount 명령어로 현재 마운트 정보 확인
            result = run_command(["mount"])
            for line in result.stdout.split("\n"):
                if device_name in line:
                    parts = line.split()
                    return {
                        "device": parts[0],
                        "mountpoint": parts[2],
                        "fstype": parts[4].strip("()"),
                        "options": parts[5].strip("()").split(",")
                    }
            return None
        except Exception:
            return None 