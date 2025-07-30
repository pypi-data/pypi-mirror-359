# DAVID L. Teams Util

[![Workflow : Publish to PyPI](https://github.com/simon-asis/teams_util/actions/workflows/PyPI.yml/badge.svg)](https://github.com/simon-asis/teams_util/actions/workflows/PyPI.yml)

[comment]: <> (This is highly site dependent package. Resources are abstracted into package structure.)
## Set Teams Workflow
##### 1) Teams Workflow 선택 (앱 검색)
##### 2) 웹후크 요청이 수신되면 채널에 게시
    ![img.png](img.png)
##### 3) 워크플로 만들기 > 흐름 만들기 (팀 / 채널 선택) > 워크플로 생성 시 Url 생성 됨. (복사)
##### 4) 워크플로 탭에서 해당 흐름을 선택 > 편집 > 템플릿 포맷 변경
```json
JSON 구문 분석 추가
콘텐츠 : 본문

{
    "type": "object",
    "properties": {
        "subject": {
            "type": "string"
        },
        "messageContent": {
            "type": "string"
        }
    }
} 

```

```text
사용자, 채널 (팀, 채널 선택)
JSON 구문에 추가한 messageContent(메시지), subject (주제) 입력
```

## Usage
Send Webhook  

```python
from teams_util.teams import send_teams_workflow_webhook

result = send_teams_workflow_webhook(webhook_url, main_title="", main_msg="")
```
It return response.status_code

## Installation

```sh
$ pip install david_teams_util --upgrade
```

If you would like to install submodules for Individual.

```sh
$ pip install david_teams_util[extra] --upgrade
```