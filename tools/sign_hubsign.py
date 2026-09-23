#!/usr/bin/env python3
"""Cherriが出力する未署名 .shortcut には次の2点が入っていない:
1) WFWorkflowName（正式な登録名。無いと表示名はファイル名から補われるだけで、
   shortcuts://run-shortcut?name=... による名前指定の起動には使われない）
2) WFWorkflowTypes に "ActionExtension"（これが無いと、iOS標準の共有シートに出てこない）
このスクリプトは、この2つを追加してから、Cherri本体と同じ手順(RoutineHubのHubSign)で署名する。
送るのはショートカットの処理内容だけで、個人用のパターン名・時刻は含まれない。"""
import argparse, json, plistlib, sys, time, urllib.error, urllib.request
from pathlib import Path

URL = "https://hubsign.routinehub.services/sign"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--share-sheet", action="store_true")
    ap.add_argument("--config-import-question", action="store_true")
    a = ap.parse_args()

    wf = plistlib.loads(a.input.read_bytes())
    before_actions = len(wf.get("WFWorkflowActions") or [])

    wf["WFWorkflowName"] = a.name

    if a.config_import_question:
        placeholder = "__ASAJITAKU_CONFIG__"
        found = None
        actions = wf.get("WFWorkflowActions") or []
        for idx, action in enumerate(actions):
            params = action.get("WFWorkflowActionParameters") or {}
            for key, value in params.items():
                if value == placeholder:
                    found = (idx, key)
                    break
            if found:
                break
        if not found:
            raise RuntimeError("config placeholder action not found")
        idx, key = found
        actions[idx]["WFWorkflowActionParameters"][key] = "{}"
        wf["WFWorkflowImportQuestions"] = [{
            "ParameterKey": key,
            "Category": "Parameter",
            "ActionIndex": idx,
            "Text": "初期設定：朝じたくの設定データを貼り付けてください",
            "DefaultValue": "{}",
        }]
        print("Config import question:", idx, key)

    if a.share_sheet:
        existing_types = list(wf.get("WFWorkflowTypes") or [])
        if "ActionExtension" not in existing_types:
            existing_types.append("ActionExtension")
        wf["WFWorkflowTypes"] = existing_types

        input_classes = list(wf.get("WFWorkflowInputContentItemClasses") or [])
        for item in ("WFStringContentItem", "WFRichTextContentItem"):
            if item not in input_classes:
                input_classes.append(item)
        wf["WFWorkflowInputContentItemClasses"] = input_classes
        wf["WFWorkflowHasShortcutInputVariables"] = True

    if len(wf.get("WFWorkflowActions") or []) != before_actions:
        raise RuntimeError("action count changed")
    if wf.get("WFWorkflowName") != a.name:
        raise RuntimeError("WFWorkflowName injection failed")
    if a.share_sheet and "ActionExtension" not in wf.get("WFWorkflowTypes", []):
        raise RuntimeError("ActionExtension injection failed")
    if a.share_sheet and "WFStringContentItem" not in wf.get("WFWorkflowInputContentItemClasses", []):
        raise RuntimeError("text input class missing")

    print("WFWorkflowName:", wf["WFWorkflowName"])
    print("ActionExtension:", "ActionExtension" in wf.get("WFWorkflowTypes", []))
    print("Text input:", "WFStringContentItem" in wf.get("WFWorkflowInputContentItemClasses", []))
    print("Action count preserved:", before_actions)

    xml = plistlib.dumps(wf, fmt=plistlib.FMT_XML, sort_keys=False).decode("utf-8")

    body = json.dumps({"shortcutName": a.name, "shortcut": xml}, ensure_ascii=False).encode("utf-8")
    last = ""
    for i in range(1, 4):
        try:
            req = urllib.request.Request(URL, data=body, method="POST", headers={
                "Content-Type": "application/json",
                "User-Agent": "cherri/2.3.0",
                "Origin": "https://routinehub.co",
                "Referer": "https://routinehub.co/"})
            with urllib.request.urlopen(req, timeout=60) as r:
                ctype = r.headers.get("Content-Type", "")
                data = r.read()
            if ctype.split(";", 1)[0] not in ("application/octet-stream", "application/x-plist", "application/x-apple-shortcut"):
                raise RuntimeError("想定外のレスポンス形式: %s" % ctype)
            if not data.startswith(b"AEA1"):
                raise RuntimeError("署名済みデータ(AEA1)ではない応答: %r" % data[:120])
            a.output.parent.mkdir(parents=True, exist_ok=True)
            a.output.write_bytes(data)
            print("OK: signed %d bytes with WFWorkflowName=%r (try %d)" % (len(data), a.name, i))
            return 0
        except urllib.error.HTTPError as e:
            last = "HTTP %s %s" % (e.code, e.read(300).decode("utf-8", "replace"))
        except Exception as e:
            last = str(e)
        print("try %d failed: %s" % (i, last), file=sys.stderr)
        time.sleep(5 * i)
    print("ERROR: HubSign signing failed: " + last, file=sys.stderr)
    return 1

if __name__ == "__main__":
    raise SystemExit(main())