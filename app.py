import requests
from bs4 import BeautifulSoup
import streamlit as st

BASE_URL = "https://estatuto.co/{}"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def descargar_y_limpiar(numero: str):
    url = BASE_URL.format(numero)
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    for tag in soup(["script", "style", "noscript", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()
        
    for lista in soup.find_all(["ul", "ol"]):
        if len(lista.find_all("a")) > 10:
            lista.decompose()
            
    titulo = f"Artículo {numero}"
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        titulo = h1.get_text(" ", strip=True)
    elif soup.title:
        titulo = soup.title.get_text(strip=True)
        
    candidatos = soup.select("article, main, #contenido, #content, .contenido, .content, .articulo")
    if not candidatos:
        candidatos = soup.find_all(["div", "section"])
        
    if candidatos:
        candidatos.sort(key=lambda el: len(el.get_text(strip=True)), reverse=True)
        mejor = next((c for c in reversed(candidatos) if len(c.get_text(strip=True)) > 200), candidatos[0])
        return titulo, mejor, url
        
    return titulo, None, url

st.set_page_config(page_title="Estatuto Tributario", page_icon="📜", layout="centered")

st.markdown("<h2 style='text-align: center; color: #1a365d;'>📜 Estatuto Tributario</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #718096;'>Consulta rápida y directa desde estatuto.co</p>", unsafe_allow_html=True)

num_articulo = st.text_input("Ingrese el número de artículo a consultar:", placeholder="Ej. 137, 188...").strip()

if num_articulo:
    with st.spinner(f"Consultando artículo {num_articulo}..."):
        try:
            titulo, contenido_html, url = descargar_y_limpiar(num_articulo)
            st.subheader(titulo)
            st.caption(f"Fuente oficial: [{url}]({url})")
            if contenido_html:
                st.markdown(str(contenido_html), unsafe_allow_html=True)
            else:
                st.warning("No se pudo estructurar el texto del artículo.")
        except Exception:
            st.error(f"No se encontró el artículo {num_articulo} o la página oficial no respondió.")
            st.markdown(f"[Intentar abrir directamente en estatuto.co/{num_articulo}](https://estatuto.co/{num_articulo})")
