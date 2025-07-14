import json
import io
import zipfile
import streamlit as st

st.set_page_config(page_title="📂 JSONL Splitter", layout="centered")
st.title("📂 JSONL Splitter")

uploaded_file = st.file_uploader("Загрузите .jsonl файл", type="jsonl")
lines_per_file = st.number_input("Строк на файл", min_value=1, value=1000)

output_format = st.radio(
    "Формат сохранения:",
    ["JSON (читабельный, с отступами)", "JSONL (в одну строку, оригинальный)"]
)

log_messages = []

def log(msg):
    log_messages.append(msg)

if uploaded_file and st.button("🚀 Разделить и скачать ZIP"):
    jsonl_lines = uploaded_file.read().decode("utf-8", errors="ignore").splitlines()
    total_lines = len(jsonl_lines)

    buffer = []
    zip_buffer = io.BytesIO()
    part_number = 1
    success_count = 0
    error_count = 0

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for idx, line in enumerate(jsonl_lines, start=1):
            try:
                obj = json.loads(line)
                buffer.append((obj, line))  # сохраняем и json, и исходник
                success_count += 1
                log(f"✅ Строка {idx}: успешно прочитана")
            except json.JSONDecodeError as e:
                error_count += 1
                log(f"❌ Строка {idx}: ошибка JSON - {str(e)}")
                continue

            if len(buffer) == lines_per_file:
                if "JSONL" in output_format:
                    content = "\n".join(orig_line for _, orig_line in buffer)
                    filename = f"part_{part_number}.jsonl"
                else:
                    content = json.dumps([obj for obj, _ in buffer], indent=2, ensure_ascii=False)
                    filename = f"part_{part_number}.json"

                zipf.writestr(filename, content)
                log(f"📦 Сохранён файл {filename} с {len(buffer)} строками")
                part_number += 1
                buffer = []

        if buffer:
            if "JSONL" in output_format:
                content = "\n".join(orig_line for _, orig_line in buffer)
                filename = f"part_{part_number}.jsonl"
            else:
                content = json.dumps([obj for obj, _ in buffer], indent=2, ensure_ascii=False)
                filename = f"part_{part_number}.json"

            zipf.writestr(filename, content)
            log(f"📦 Сохранён файл {filename} с {len(buffer)} строками")

    zip_buffer.seek(0)
    st.success(f"✅ Завершено: строк прочитано: {total_lines}, успешно: {success_count}, ошибок: {error_count}, файлов: {part_number}")

    st.download_button(
        label="📥 Скачать ZIP архив",
        data=zip_buffer,
        file_name="jsonl_parts.zip",
        mime="application/zip"
    )

    with st.expander("📋 Показать логи"):
        st.text("\n".join(log_messages))
