# Ubuntu RAID CLI

Ubuntu 시스템에서 RAID 구성을 쉽게 관리할 수 있는 CLI 도구입니다.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+"/>
  <img src="https://img.shields.io/badge/OS-Ubuntu%2020.04+-orange.svg" alt="Ubuntu 20.04+"/>
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT"/>
</p>

**Ubuntu RAID CLI**는 이미 존재하는 mdadm 및 기타 도구를 사용하여 필요한 디스크 레이드, 초기화, 검사 등을 대리하여 수행하는 CLI 도구입니다. 이미 존재하는 CLI 도구들을 사용하도록 만든 도구이지만 혹여나 문제가 발생하는 경우 버그픽스를 위해 관련 정보를 공유해주시기 바랍니다.

이메일: im@devcomfort.me

## 목차

- [개요](#개요)
- [일반 사용자 가이드](#일반-사용자-가이드)
  - [주요 기능](#주요-기능)
  - [시스템 요구사항](#시스템-요구사항)
  - [설치 및 삭제](#설치-및-삭제)
  - [업데이트](#업데이트)
  - [기본 사용법](#기본-사용법)
  - [사용 예시](#사용-예시)
  - [주의사항](#주의사항)
- [개발자 가이드](#개발자-가이드)
  - [개발 환경 설정](#개발-환경-설정)
  - [프로젝트 구조](#프로젝트-구조)
  - [빌드 및 배포](#빌드-및-배포)
  - [테스트](#테스트)
  - [기여 방법](#기여-방법)
- [문제 해결](#문제-해결)
- [지원 및 피드백](#지원-및-피드백)
- [라이선스](#라이선스)

---

## 개요

**Ubuntu RAID CLI**는 시스템 관리자와 일반 사용자 모두가 Ubuntu 환경에서 RAID 배열을 쉽게 관리할 수 있도록 설계된 명령줄 인터페이스 도구입니다. 이 도구는 mdadm과 같은 기존 Linux 시스템 유틸리티를 활용하여 복잡한 RAID 작업을 단순화합니다.

---

# 일반 사용자 가이드

## 주요 기능

- **디스크 관리**: 시스템의 모든 디스크 목록 확인 및 상태 관리
- **RAID 설정**: RAID 0, 1, 5, 6 배열 생성 및 관리
- **자동 추천**: 디스크 수와 크기에 따른 최적의 RAID 레벨 추천
- **마운트 관리**: RAID 및 디스크의 마운트 위치 설정 및 변경
- **상태 모니터링**: 디스크 및 RAID 배열의 건강 상태 실시간 확인
- **파일 시스템 관리**: 장치 포맷, 마운트, 언마운트 등의 관리 기능

## 시스템 요구사항

- Ubuntu 20.04 이상
- Python 3.8 이상
- mdadm, smartmontools 패키지 (자동으로 설치됨)

## 설치 및 삭제

### 1. pip를 이용한 설치

```bash
sudo pip install git+https://github.com/devcomfort/ubuntu-raid-cli.git
```

### 2. 소스코드에서 직접 설치

```bash
git clone https://github.com/devcomfort/ubuntu-raid-cli.git
cd ubuntu-raid-cli
sudo pip install .
```

설치가 완료되면 `raid` 명령어를 바로 사용할 수 있습니다.

### 삭제 방법

패키지를 삭제하려면 다음 명령어를 실행하세요:

```bash
sudo pip uninstall ubuntu-raid-cli
```

## 업데이트

최신 버전으로 업데이트하려면 다음 명령어를 실행하세요:

```bash
raid update
```

이 명령어는 GitHub 저장소에서 최신 버전을 가져와 자동으로 업데이트합니다. 업데이트 전후의 버전 정보도 함께 표시됩니다.

## 기본 사용법

설치 후 `raid` 명령어를 사용하여 도구를 실행할 수 있습니다:

```bash
# 도움말 표시
raid --help

# 디스크 목록 확인
raid list-disks

# RAID 배열 목록 확인
raid list-raids

# RAID 설정 (대화형)
raid setup-raid

# 상태 확인
raid check
```

독립 실행형 배포판을 사용한 경우 `raid-cli` 명령어를 사용합니다:

```bash
# 도움말 표시
raid-cli --help

# 디스크 목록 확인
raid-cli list-disks
```

## 사용 예시

### RAID 5 배열 생성

```bash
# 대화형으로 RAID 5 설정
raid setup-raid --level 5 --device /dev/md0 --mount /mnt/raid5
```

### 디스크 상태 확인

```bash
# 전체 디스크 상태 확인
raid check

# 특정 디스크 확인
raid check --device /dev/sda
```

### 포맷 및 마운트

```bash
# 장치 포맷
raid format-device

# 장치 마운트
raid mount-device

# 장치 재마운트 (fstab 설정 업데이트)
raid remount-device
```

재마운트 기능은 다음과 같은 경우에 유용합니다:
- fstab 설정이 변경된 경우
- 마운트 옵션이 업데이트된 경우
- 시스템 안정성 설정이 변경된 경우
- 디바이스의 마운트 상태를 새로고침하고 싶은 경우

## 주의사항

- **데이터 손실 위험**: RAID 설정은 디스크의 모든 데이터를 삭제합니다. 중요한 데이터는 미리 백업하세요.
- **권한 요구사항**: 대부분의 RAID 관련 작업은 root 권한이 필요합니다.
- **RAID 레벨별 최소 디스크 수**:
  - RAID 0: 2개 이상 (데이터 보호 없음, 성능 향상)
  - RAID 1: 2개 이상 (미러링, 50% 용량 효율)
  - RAID 5: 3개 이상 (패리티, 1개 디스크 장애 허용)
  - RAID 6: 4개 이상 (이중 패리티, 2개 디스크 장애 허용)
- **하드웨어 호환성**: 모든 디스크가 SMART 기능을 지원하지 않을 수 있습니다.
- **경고 사항**: 비정상적인 SMART 값이 발견되면 즉시 데이터를 백업하고 디스크 교체를 고려하세요.
- **시스템 안정성**:
  - RAID 디스크는 자동으로 fstab에 안정적인 옵션으로 설정됩니다.
  - RAID 1, 5, 6: `nofail,x-systemd.device-timeout=5` 옵션 적용
  - RAID 0: `nofail,x-systemd.device-timeout=3` 옵션 적용
  - fstab 설정 전 자동으로 백업 파일이 생성됩니다.

---

# 개발자 가이드

## 개발 환경 설정

### 필수 요구사항

- Python 3.8 이상
- Rye 패키지 관리자
- mdadm, smartmontools 패키지

### 개발 환경 구성

```bash
# 프로젝트 클론
git clone https://github.com/devcomfort/ubuntu-raid-cli.git
cd ubuntu-raid-cli

# Rye로 개발 환경 구성
rye sync --dev
```

## 프로젝트 구조

```
ubuntu-raid-cli/
├── src/
│   └── ubuntu_raid_cli/   # 메인 패키지
│       ├── __init__.py
│       ├── cli.py         # CLI 인터페이스
│       ├── main.py        # 진입점
│       ├── raid_manager.py # RAID 관리
│       └── utils.py       # 유틸리티
├── scripts/               # 빌드/설치 스크립트
├── tests/                # 테스트 코드
├── pyproject.toml        # 프로젝트 설정
└── README.md
```

## 빌드 및 배포

Rye를 사용한 빌드:

```bash
# 개발 의존성 포함 동기화
rye sync --dev

# 프로젝트 빌드
rye build
```

빌드된 패키지는 `dist/` 디렉토리에 생성됩니다.

## 테스트

테스트 실행:

```bash
# 모든 테스트 실행
pytest

# 특정 테스트 실행
pytest tests/test_raid_manager.py
```

## 기여 방법

1. 이슈 확인 또는 새 이슈 생성
2. 프로젝트 포크
3. 기능/버그 수정 브랜치 생성 (`git checkout -b feature/amazing-feature`)
4. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
5. 원격 저장소에 푸시 (`git push origin feature/amazing-feature`)
6. Pull Request 생성

코드 스타일은 Black과 isort를 따릅니다:
```bash
# 코드 포맷팅
black src/
isort src/

# 타입 체크
mypy src/
```

---

# 문제 해결

## 일반적인 문제와 해결 방법

### RAID 생성 실패
- **원인**: 디스크가 이미 다른 용도로 사용 중이거나, 파티션 테이블에 문제가 있을 수 있습니다.
- **해결**: 
  ```bash
  # 자세한 디스크 정보 확인
  raid list-disks -v
  
  # 기존 파티션 및 RAID 정보 제거
  sudo wipefs -a /dev/sdX
  ```

### 마운트 오류
- **원인**: 파일 시스템이 올바르게 포맷되지 않았거나, 마운트 포인트 디렉토리가 없는 경우입니다.
- **해결**:
  ```bash
  # 장치 다시 포맷
  raid format-device --device /dev/mdX --filesystem ext4
  
  # 마운트 포인트 수동 생성
  sudo mkdir -p /mnt/raidX
  ```

### 부팅 시 마운트 실패
- **원인**: fstab 설정이 올바르지 않거나, 디바이스가 부팅 시점에 준비되지 않은 경우입니다.
- **해결**:
  ```bash
  # fstab 설정 확인 및 재마운트
  raid remount-device --device /dev/mdX --mount /mnt/raidX
  ```

### 권한 문제
- **원인**: 대부분의 RAID 관련 작업은 root 권한이 필요합니다.
- **해결**: 명령어 앞에 `sudo`를 붙여 실행하세요.

## 진단 명령어

문제 진단을 위한 유용한 명령어들:

```bash
# RAID 상태 확인
cat /proc/mdstat
sudo mdadm --detail /dev/mdX

# 디스크 상태 확인
sudo smartctl -a /dev/sdX

# 시스템 로그 확인
sudo journalctl -u mdmonitor
```

## 오류 코드

자주 발생하는 오류 코드와 의미:

| 코드 | 설명 | 해결 방법 |
|------|------|----------|
| E001 | 디스크 접근 권한 부족 | sudo로 실행 |
| E002 | 지원되지 않는 RAID 레벨 | 올바른 RAID 레벨 지정 |
| E003 | 디스크 수 부족 | 해당 RAID 레벨에 필요한 최소 디스크 수 확인 |
| E004 | 마운트 포인트 문제 | 디렉토리 존재 여부 및 권한 확인 |

---

# 지원 및 피드백

## 도움 받기

문제가 발생하거나 질문이 있는 경우 다음 방법으로 도움을 받을 수 있습니다:

1. **GitHub 이슈**: [이슈 페이지](https://github.com/devcomfort/ubuntu-raid-cli/issues)에서 새 이슈를 생성하세요.
2. **이메일**: 심각한 버그나 보안 문제는 직접 이메일(im@devcomfort.me)로 연락주세요.

## 기능 요청

새로운 기능을 제안하고 싶다면 GitHub 이슈를 통해 기능 요청을 제출해 주세요. 기능 요청 시 다음 정보를 포함하면 도움이 됩니다:

- 기능에 대한 자세한 설명
- 사용 사례 및 예시
- 관련 참고 자료나 문서

## RAID 관련 추가 자료

RAID 기술과 mdadm 사용법에 대한 더 자세한 정보는 다음 자료를 참고하세요:

- [Linux RAID Wiki](https://raid.wiki.kernel.org/)
- [Ubuntu Server 가이드 - RAID](https://ubuntu.com/server/docs/devices-storage-raid)
- [mdadm 매뉴얼](https://man7.org/linux/man-pages/man8/mdadm.8.html)

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
