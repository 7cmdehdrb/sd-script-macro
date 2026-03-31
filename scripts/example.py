import os
import json
import random
import re
from datetime import datetime
import modules.scripts as scripts
import gradio as gr
from modules.processing import process_images, Processed
from modules.shared import state

EXT_DIR = os.path.dirname(os.path.abspath(__file__))
PRESETS_PATH = os.path.join(EXT_DIR, "presets_v5.json")
HISTORY_PATH = os.path.join(EXT_DIR, "macro_history.json")

# 시스템 전체를 지배하는 절대적인 카테고리 디폴트 순서
CATEGORIES = ["character", "main", "cloth", "place", "base", "etc"]

def load_presets():
    default_data = {c: {} for c in CATEGORIES}
    if not os.path.exists(PRESETS_PATH):
        return default_data
    try:
        with open(PRESETS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            for c in default_data.keys():
                if c not in data:
                    data[c] = {}
            return data
    except:
        return default_data

def save_presets(data):
    with open(PRESETS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def update_view():
    data = load_presets()
    res = ""
    for cat in CATEGORIES:
        res += f"[{cat.upper()}]\n"
        if not data[cat]:
            res += "  (비어 있음)\n"
        for k, v in data[cat].items():
            res += f"  - {k} | 긍정: {v.get('pos','')} | 부정: {v.get('neg','')}\n"
        res += "\n"
    return res

def generate_cheat_sheet():
    data = load_presets()
    md = "### 📚 사용 가능한 프롬프트 이름표\n"
    md += "*(스케줄러에 아래 이름들을 적으세요)*\n\n"
    for cat in CATEGORIES:
        keys = list(data[cat].keys())
        if keys:
            md += f"- **{cat.upper()}**: {', '.join(keys)}\n"
        else:
            md += f"- **{cat.upper()}**: (없음)\n"
    return md

def load_history():
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_to_history(t_pos, t_neg, sched):
    data = load_history()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [l for l in sched.split("\n") if l.strip() and ":" in l]
    summary = lines[0][:30] + "..." if lines else "빈 스케줄"
    label = f"[{now_str}] {summary} (총 {len(lines)}줄)"

    entry = {
        "label": label,
        "template_pos": t_pos,
        "template_neg": t_neg,
        "schedule": sched,
    }
    data.insert(0, entry)
    data = data[:20]

    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_history_choices():
    data = load_history()
    return [item["label"] for item in data]

class Script(scripts.Script):
    def title(self):
        return "Min's Master Macro V14"

    def show(self, is_img2img):
        return True

    def ui(self, is_img2img):
        with gr.Tabs():
            with gr.TabItem("🧩 프롬프트 조각 관리"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 💾 조각 저장 / 삭제")
                        cat_radio = gr.Radio(choices=CATEGORIES, value=None, label="카테고리 선택")
                        frag_name = gr.Textbox(label="조각 이름표 (띄어쓰기 가능, 쉼표 불가)", lines=1)
                        frag_pos = gr.Textbox(label="🟢 긍정 프롬프트 (Positive)", lines=2)
                        frag_neg = gr.Textbox(label="🔴 부정 프롬프트 (Negative)", lines=2)

                        with gr.Row():
                            save_btn = gr.Button("💾 저장 / 덮어쓰기", variant="primary")
                            delete_btn = gr.Button("🗑️ 조각 삭제", variant="stop")

                    with gr.Column(scale=1):
                        with gr.Row():
                            gr.Markdown("### 📋 현재 저장된 상세 내용")
                            refresh_view_btn = gr.Button("🔄 새로고침", size="sm")
                        view_area = gr.Textbox(label="목록", lines=15, interactive=False, value=update_view)

            with gr.TabItem("🎬 스케줄러 (실행)"):
                with gr.Accordion("📜 최근 실행 기록 불러오기 (최대 20개)", open=False):
                    with gr.Row():
                        history_dropdown = gr.Dropdown(label="복원할 로그 선택", choices=get_history_choices(), interactive=True)
                        refresh_history_btn = gr.Button("🔄 목록 새로고침")
                        apply_history_btn = gr.Button("✅ 템플릿 및 스케줄에 적용", variant="primary")

                gr.HTML("<hr>")

                with gr.Row():
                    with gr.Column(scale=7):
                        gr.Markdown("### ⚙️ 1. 프롬프트 조립 순서")
                        with gr.Row():
                            template_pos = gr.Textbox(label="🟢 긍정 템플릿", value="{character}, {main}, {cloth}, {place}, {base}, {etc}", lines=1, elem_id="min_t_pos_v14")
                            template_neg = gr.Textbox(label="🔴 부정 템플릿", value="{character}, {main}, {cloth}, {place}, {base}, {etc}", lines=1, elem_id="min_t_neg_v14")

                        gr.Markdown("### 🚀 2. 스케줄 입력")
                        schedule_input = gr.Textbox(
                            label="스케줄 (반복횟수 : 템플릿 순서 + 긍정 태그 | 부정 태그)",
                            lines=10,
                            placeholder="3 : char1, main1, cloth1, place1, base1, none, happy | ugly",
                            info="템플릿 개수(6개) 초과 단어들은 맨 뒤에 붙습니다. '|'를 쓰면 앞은 긍정, 뒤는 부정에 추가됩니다.",
                        )

                    with gr.Column(scale=3):
                        cheat_sheet = gr.Markdown(value=generate_cheat_sheet())

        def on_refresh_all():
            return update_view(), generate_cheat_sheet()

        refresh_view_btn.click(fn=on_refresh_all, outputs=[view_area, cheat_sheet])

        def on_save(cat, name, pos, neg):
            if not cat or not name.strip():
                return update_view(), generate_cheat_sheet(), gr.update(), gr.update(), gr.update()
            data = load_presets()
            if cat not in data:
                data[cat] = {}
            data[cat][name.strip()] = {"pos": pos.strip(), "neg": neg.strip()}
            save_presets(data)
            return update_view(), generate_cheat_sheet(), gr.update(value=""), gr.update(value=""), gr.update(value="")

        save_btn.click(fn=on_save, inputs=[cat_radio, frag_name, frag_pos, frag_neg], outputs=[view_area, cheat_sheet, frag_name, frag_pos, frag_neg])

        def on_delete(cat, name):
            if cat == "CANCEL_ACTION" or not cat:
                return gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
            name_key = name.strip()
            if not name_key:
                return update_view(), generate_cheat_sheet(), gr.update(), gr.update(), gr.update()
            data = load_presets()
            if cat in data and name_key in data[cat]:
                del data[cat][name_key]
                save_presets(data)
            return update_view(), generate_cheat_sheet(), gr.update(value=""), gr.update(value=""), gr.update(value="")

        delete_btn.click(
            fn=on_delete, inputs=[cat_radio, frag_name], outputs=[view_area, cheat_sheet, frag_name, frag_pos, frag_neg],
            _js="function(cat, name){ return confirm(`정말 '${name}' 조각을 삭제하시겠습니까?`) ? [cat, name] : ['CANCEL_ACTION', 'CANCEL_ACTION']; }"
        )

        def on_refresh_history():
            choices = get_history_choices()
            return gr.update(choices=choices, value=choices[0] if choices else None)

        refresh_history_btn.click(fn=on_refresh_history, outputs=[history_dropdown])

        def on_apply_history(selected_label):
            if not selected_label:
                return gr.update(), gr.update(), gr.update()
            for item in load_history():
                if item["label"] == selected_label:
                    return gr.update(value=item["template_pos"]), gr.update(value=item["template_neg"]), gr.update(value=item["schedule"])
            return gr.update(), gr.update(), gr.update()

        apply_history_btn.click(fn=on_apply_history, inputs=[history_dropdown], outputs=[template_pos, template_neg, schedule_input])

        return [template_pos, template_neg, schedule_input]

    def run(self, p, template_pos, template_neg, schedule_input):
        data = load_presets()
        lines = [l.strip() for l in schedule_input.split("\n") if l.strip() and ":" in l]

        keys_in_order = re.findall(r"\{([a-zA-Z0-9_]+)\}", template_pos)
        if not keys_in_order:
            print("[Min's Scheduler] 오류: 긍정 템플릿에 { } 형태의 변수가 없습니다.")
            return process_images(p)

        final_tasks = []

        for line in lines:
            count_str, frags_str = line.split(":", 1)
            try:
                count = int("".join(filter(str.isdigit, count_str)))
            except:
                continue

            frag_names = [x.strip() for x in frags_str.split(",")]

            # [🔥 V14 신규] 지정된 템플릿 개수를 초과하는 나머지 단어들 수집 및 긍정/부정 분리
            extra_tags_list = frag_names[len(keys_in_order):]
            extra_tags_raw = ",".join(extra_tags_list)
            
            if "|" in extra_tags_raw:
                pos_extra, neg_extra = extra_tags_raw.split("|", 1)
            else:
                pos_extra = extra_tags_raw
                neg_extra = ""
                
            pos_extra_str = ", ".join([x.strip() for x in pos_extra.split(",") if x.strip() and x.strip().lower() != 'none'])
            neg_extra_str = ", ".join([x.strip() for x in neg_extra.split(",") if x.strip() and x.strip().lower() != 'none'])

            while len(frag_names) < len(keys_in_order):
                frag_names.append("")

            input_map = {
                key: name
                for key, name in zip(keys_in_order, frag_names[: len(keys_in_order)])
            }

            def get_text(cat, name, is_pos=True):
                if not name or name.lower() == "none":
                    return ""
                cat_data = data.get(cat, {})
                if name in cat_data:
                    return cat_data[name].get("pos" if is_pos else "neg", "")
                else:
                    return name if is_pos else ""

            kwargs_pos = {k: get_text(k, input_map[k], True) for k in keys_in_order}
            kwargs_neg = {k: get_text(k, input_map[k], False) for k in keys_in_order}

            try:
                raw_pos = template_pos.format(**kwargs_pos)
                raw_neg = template_neg.format(**kwargs_neg)
            except KeyError as e:
                print(f"[Min's Scheduler] 템플릿 포맷팅 오류: {e} 변수가 매핑되지 않았습니다.")
                continue

            # [🔥 V14 신규] 파이프(|)로 분리된 추가 꼬리표를 각각의 프롬프트 맨 뒤에 주입
            if pos_extra_str:
                raw_pos += ", " + pos_extra_str
            if neg_extra_str:
                raw_neg += ", " + neg_extra_str

            cleaned_pos = ", ".join([x.strip() for x in raw_pos.split(",") if x.strip()])
            cleaned_neg = ", ".join([x.strip() for x in raw_neg.split(",") if x.strip()])

            final_tasks.extend([(cleaned_pos, cleaned_neg)] * count)

        if not final_tasks:
            print("[Min's Scheduler] 파싱된 스케줄이 없습니다.")
            return process_images(p)

        save_to_history(template_pos, template_neg, schedule_input)

        p.do_not_save_grid = True
        state.job_count = len(final_tasks)

        all_images = []
        all_prompts = []
        all_negative_prompts = []
        all_seeds = []
        infotexts = []

        print(f"\n[Min's Scheduler] V14: 총 {len(final_tasks)}장의 이미지 스케줄링을 시작합니다.")

        for i, (current_pos, current_neg) in enumerate(final_tasks):
            if state.interrupted:
                break

            print(f" -> [{i+1}/{len(final_tasks)}] Pos: {current_pos[:30]}... | Neg: {current_neg[:30]}...")

            p.prompt = current_pos
            p.negative_prompt = current_neg
            p.all_prompts = [current_pos]
            p.all_negative_prompts = [current_neg]
            p.n_iter = 1
            p.batch_size = 1

            p.seed = random.randint(0, 2147483647)
            p.subseed = -1

            proc = process_images(p)

            all_images.extend(proc.images)
            all_prompts.extend(proc.all_prompts)
            all_negative_prompts.extend(proc.all_negative_prompts)
            all_seeds.extend(proc.all_seeds)
            infotexts.extend(proc.infotexts)

        return Processed(
            p,
            all_images,
            all_seeds[0] if all_seeds else -1,
            "",
            all_prompts=all_prompts,
            all_negative_prompts=all_negative_prompts,
            all_seeds=all_seeds,
            infotexts=infotexts,
        )