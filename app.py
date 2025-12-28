import streamlit as st
import xml.etree.ElementTree as ET
import re

st.set_page_config(page_title="XML Corpus Triage Tool", layout="centered")

st.title("🧪 XML Corpus Triage Tool")
st.caption(
    "Checks whether a corpus is valid XML, repairable XML, or must be treated as plain text."
)

uploaded = st.file_uploader("Upload corpus file", type=["xml", "txt"])

# -------------------------------
# Utilities
# -------------------------------

def is_well_formed(xml_text):
    try:
        ET.fromstring(xml_text)
        return True
    except ET.ParseError:
        return False


def repair_xml(xml_text):
    """
    Aggressive but safe XML repair for corpus data
    """
    # Escape bare ampersands
    xml_text = re.sub(r'&(?![a-zA-Z]+;)', '&amp;', xml_text)

    # Remove illegal control characters
    xml_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', xml_text)

    xml_text = xml_text.strip()

    # Must look like XML at least a bit
    if "<" not in xml_text or ">" not in xml_text:
        return None

    # Wrap in root
    xml_text = f"<root>{xml_text}</root>"

    try:
        ET.fromstring(xml_text)
        return xml_text
    except ET.ParseError:
        return None


def strip_to_plain_text(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# -------------------------------
# Main logic
# -------------------------------

if uploaded:
    raw_text = uploaded.read().decode("utf-8", errors="ignore")

    st.subheader("📋 Analysis Result")

    if is_well_formed(raw_text):
        st.success("✅ Well-formed XML")
        final_text = raw_text
        mode = "xml"

    else:
        repaired = repair_xml(raw_text)

        if repaired:
            st.warning("⚠️ XML repaired automatically")
            final_text = repaired
            mode = "xml_repaired"

        else:
            st.error("❌ Not valid XML — converted to plain text")
            final_text = strip_to_plain_text(raw_text)
            mode = "plain_text"

    st.subheader("🔎 Preview")
    st.code(final_text[:3000], language="xml" if mode.startswith("xml") else "text")

    st.subheader("⬇️ Download normalized corpus")

    st.download_button(
        "Download processed corpus",
        final_text,
        file_name=f"normalized_{uploaded.name}",
    )
