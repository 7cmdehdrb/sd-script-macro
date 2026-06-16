# Min's Master Macro V14

SD-webUI-ReForge에서 프롬프트 조각을 저장하고, 스케줄에 따라 여러 이미지를 순차 생성하기 위한 확장 기능입니다.

캐릭터, 동작, 의상, 장소, 품질 태그 등을 미리 조각으로 저장한 뒤, 스케줄 입력만으로 여러 프롬프트 조합을 자동 실행할 수 있습니다.

## 주요 기능

- 프롬프트 조각 저장 및 삭제
- Positive / Negative 프롬프트 동시 관리
- 카테고리 기반 프롬프트 조립
- 스케줄 기반 이미지 반복 생성
- 추가 Positive / Negative 태그 입력 지원
- 최근 실행 기록 최대 20개 저장 및 복원
- 이미지마다 랜덤 시드 자동 적용

## 카테고리

프롬프트 조각은 아래 카테고리로 관리됩니다.

```text
character
main
cloth
place
base
etc
```

기본 템플릿은 이 순서를 기준으로 구성됩니다.

```text
{character}, {main}, {cloth}, {place}, {base}, {etc}
```

## 설치 방법

확장 스크립트 파일을 SD-webUI-ReForge의 extension scripts 폴더에 넣습니다.

예시 구조:

```text
stable-diffusion-webui-reforge/
└── extensions/
    └── mins-master-macro/
        └── scripts/
            └── mins_master_macro.py
```

이후 WebUI를 재시작하면 Script 영역에서 아래 항목을 선택할 수 있습니다.

```text
Min's Master Macro V14
```

## 사용 방법

### 1. 프롬프트 조각 저장

`프롬프트 조각 관리` 탭에서 프롬프트 조각을 저장합니다.

입력 항목은 다음과 같습니다.

```text
카테고리
조각 이름표
Positive 프롬프트
Negative 프롬프트
```

예시:

```text
카테고리: character
조각 이름표: girl1
Positive: 1girl, solo, long hair
Negative: old, male
```

저장된 조각은 스케줄러에서 이름표로 호출할 수 있습니다.

## 2. 템플릿 설정

`스케줄러 (실행)` 탭에서 프롬프트 조립 순서를 설정합니다.

기본 Positive 템플릿:

```text
{character}, {main}, {cloth}, {place}, {base}, {etc}
```

기본 Negative 템플릿:

```text
{character}, {main}, {cloth}, {place}, {base}, {etc}
```

템플릿의 `{character}`, `{main}` 같은 항목은 각 카테고리에 저장된 조각 이름과 매칭됩니다.

## 3. 스케줄 입력

스케줄은 한 줄에 하나씩 작성합니다.

기본 형식:

```text
반복횟수 : character, main, cloth, place, base, etc, 추가 Positive 태그 | 추가 Negative 태그
```

예시:

```text
3 : girl1, pose1, dress1, room1, quality1, none, smiling, looking at viewer | bad hands, blurry
```

위 예시는 다음과 같이 처리됩니다.

```text
생성 수: 3장

character: girl1
main: pose1
cloth: dress1
place: room1
base: quality1
etc: none

추가 Positive 태그:
smiling, looking at viewer

추가 Negative 태그:
bad hands, blurry
```

## 스케줄 작성 예시

```text
2 : girl1, standing, casual, street, best_quality, none
3 : girl1, sitting, dress, cafe, best_quality, none, smile | bad hands
1 : boy1, running, uniform, school, anime_style, none, dynamic pose | low quality, blurry
```

각 줄은 독립적인 이미지 생성 작업으로 처리됩니다.

## 특수 규칙

### none

해당 위치의 프롬프트 조각을 비우고 싶을 때 사용합니다.

```text
1 : girl1, main1, none, room1, base1, none
```

### 파이프 기호 `|`

`|` 앞쪽은 Positive 추가 태그로 들어갑니다.

`|` 뒤쪽은 Negative 추가 태그로 들어갑니다.

예시:

```text
1 : girl1, pose1, cloth1, place1, base1, none, smile | bad anatomy
```

처리 결과:

```text
Positive 끝에 추가:
smile

Negative 끝에 추가:
bad anatomy
```

## 실행 방식

스케줄을 입력하고 이미지를 생성하면, extension은 각 줄을 순서대로 해석합니다.

각 작업마다 다음 처리를 수행합니다.

```text
1. 스케줄 한 줄 파싱
2. 카테고리별 조각 이름 확인
3. 저장된 Positive / Negative 프롬프트 불러오기
4. 템플릿에 맞게 프롬프트 조립
5. 추가 태그 병합
6. 지정된 반복 횟수만큼 이미지 생성
7. 각 이미지마다 랜덤 seed 적용
```

## 최근 실행 기록

실행한 템플릿과 스케줄은 `macro_history.json`에 저장됩니다.

최근 기록은 최대 20개까지 유지됩니다.

`최근 실행 기록 불러오기` 메뉴에서 이전 스케줄을 선택한 뒤 다시 적용할 수 있습니다.

## 저장 파일

이 extension은 실행 폴더에 다음 파일을 생성하거나 사용합니다.

```text
presets_v5.json
macro_history.json
```

각 파일의 역할은 다음과 같습니다.

```text
presets_v5.json
- 저장된 프롬프트 조각 데이터

macro_history.json
- 최근 실행한 템플릿 및 스케줄 기록
```

## 주의사항

- 조각 이름에는 쉼표를 사용하지 않는 것이 좋습니다.
- 스케줄 한 줄에는 반드시 `:`가 포함되어야 합니다.
- 반복 횟수는 숫자로 해석 가능한 형태여야 합니다.
- 템플릿에는 `{character}`처럼 중괄호 형태의 변수가 포함되어야 합니다.
- 저장되지 않은 조각 이름을 입력하면 Positive 쪽에는 해당 이름이 그대로 들어갑니다.
- 저장되지 않은 조각 이름은 Negative 쪽에는 반영되지 않습니다.
- 이미지마다 seed는 자동으로 랜덤 지정됩니다.
- Grid 이미지는 저장하지 않고 개별 생성 결과를 반환합니다.

## 간단 예시

### 저장된 조각

```text
[character]
girl1
Positive: 1girl, solo
Negative: male

[main]
sitting
Positive: sitting, looking at viewer
Negative: standing

[base]
best_quality
Positive: best quality, masterpiece
Negative: low quality, worst quality
```

### 스케줄

```text
2 : girl1, sitting, none, cafe, best_quality, none, smile | bad hands
```

### 생성되는 프롬프트 예시

Positive:

```text
1girl, solo, sitting, looking at viewer, cafe, best quality, masterpiece, smile
```

Negative:

```text
male, standing, low quality, worst quality, bad hands
```

## 요약

Min's Master Macro V14는 자주 사용하는 프롬프트를 조각 단위로 저장하고, 스케줄 입력을 통해 여러 이미지 생성 작업을 자동화하는 SD-webUI-ReForge용 매크로 확장입니다.

반복적인 프롬프트 조합 작업을 줄이고, 캐릭터 / 동작 / 의상 / 장소 / 품질 태그 등을 체계적으로 관리하는 데 사용할 수 있습니다.