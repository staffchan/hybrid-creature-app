import streamlit as st

st.set_page_config(
    page_title="キメラプロンプト生成",
    layout="centered"
)
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(
                        circle at 50% 15%, 
                        rgba(255, 255, 210, 0.25), 
                        rgba(30, 30, 47, 0.9) 60%
                    ),
                    linear-gradient(
                        to bottom, 
                        #1e1e2f 0%, 
                        #161622 100%
                    );
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    [data-testid="stAppViewContainer"] * {
        color: #f0f8ff;
        font-family: 'serif';
    }
    </style>
    """,
    unsafe_allow_html=True
)
from animal_traits import animal_traits_ja, animal_traits_en

st.title("キメラ融合プロンプト生成アプリ")
st.markdown("2体の動物を選ぶと、融合されたクリーチャーの英語・日本語プロンプトが生成されます。")

animals = list(animal_traits_ja.keys())
animal1 = st.selectbox("動物①を選んでください", animals)
animal2 = st.selectbox("動物②を選んでください", animals, index=1)

def generate_prompt(animal1, animal2):
    a1_ja, a2_ja = animal_traits_ja[animal1], animal_traits_ja[animal2]
    a1_en, a2_en = animal_traits_en[animal1], animal_traits_en[animal2]

    prompt_en = f"""
A mythical chimera combining the {a1_en["vibe"]} of a {a1_en["name"]} and the {a2_en["vibe"]} of a {a2_en["name"]}.
Its body is {a1_en["body"]}, with {a2_en["limbs"]}.
The texture is {a1_en["texture"]}, and it moves by {a2_en["movement"]}.
This creature is found in {a1_en["habitat"]}, and displays traits of both its origins.
Cinematic lighting, natural environment, fantasy realism. --ar 9:16
""".strip()

    prompt_ja = f"""
{animal1}の{a1_ja["特徴"]}と、{animal2}の{a2_ja["特徴"]}を融合した神秘的なキメラ。
体型は{a1_ja["体型"]}、手足は{a2_ja["脚"]}。
肌の質感は{a1_ja["肌"]}で、動きは{a2_ja["動き"]}。
生息地は{a1_ja["環境"]}で、両方の特徴を兼ね備えている。
シネマ風ライティング、自然な背景、幻想的なリアル感。--ar 9:16
""".strip()

    return prompt_en, prompt_ja

if st.button("プロンプト生成"):
    en, ja = generate_prompt(animal1, animal2)
    st.subheader("英語プロンプト")
    st.code(en, language="text")
    st.subheader("日本語プロンプト")
    st.code(ja, language="text")

import os
import openai
from openai import OpenAI

st.header("🧠 動物名からキメラ候補をAI補完で追加")

new_animal_name = st.text_input("追加したい動物名（日本語）を入力してください")

if st.button("AIで動物を追加"):
    if new_animal_name:
        with st.spinner("AIが特徴を考え中..."):
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

            prompt = f"""
あなたは動物辞書の設計者です。
以下の動物について、6つの特徴を日本語と英語でそれぞれ出力してください。

## 出力形式（辞書として構成してください）:
animal_traits_ja = {{
    "{new_animal_name}": {{
        "体型": "...",
        "脚": "...",
        "特徴": "...",
        "肌": "...",
        "動き": "...",
        "環境": "..."
    }}
}}

animal_traits_en = {{
    "{new_animal_name}": {{
        "name": "...",
        "body": "...",
        "limbs": "...",
        "vibe": "...",
        "texture": "...",
        "movement": "...",
        "habitat": "..."
    }}
}}
"""

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,
                )
                generated = response.choices[0].message.content

                local_vars = {}
                exec(generated, {}, local_vars)

                animal_traits_ja.update(local_vars.get("animal_traits_ja", {}))
                animal_traits_en.update(local_vars.get("animal_traits_en", {}))

                st.success(f"{new_animal_name} を辞書に追加しました！")
            except Exception as e:
                st.error(f"生成中にエラーが発生しました: {e}")
    else:
        st.warning("動物名を入力してください")
