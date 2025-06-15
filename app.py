import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from urllib.parse import quote
import zipfile

st.set_page_config(page_title="Generador de Etiquetas QR", layout="centered")

st.title("📦 Generador de Etiquetas con QR")

uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

pbs_logo = st.file_uploader("Logo PBS (.jpg)", type=["jpg"])
xerox_logo = st.file_uploader("Logo Xerox (.jpg)", type=["jpg"])

if uploaded_file and pbs_logo and xerox_logo:
    df = pd.read_csv(uploaded_file, sep=';')

    WIDTH, HEIGHT = 4 * inch, 3 * inch
    output = BytesIO()
    c = canvas.Canvas(output, pagesize=(WIDTH, HEIGHT))

    for _, row in df.iterrows():
        serie = str(row["Serie"])
        modelo = str(row["Modelo"])
        cliente = str(row["Nombre del Cliente"])

        mensaje = f"Hola, soy de Nicaragua, me gustaria reportar mi equipo con serie {serie}, Modelo {modelo}, por la siguiente razón:"
        whatsapp_url = f"https://wa.me/50584147953?text={quote(mensaje)}"

        asunto = f"Equipo serie {serie}"
        cuerpo = mensaje
        email_url = f"mailto:callcenter.ni@pbs.group?subject={quote(asunto)}&body={quote(cuerpo)}"

        def generar_qr(data):
            qr = qrcode.make(data)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            buffer.seek(0)
            return ImageReader(buffer)

        qr_img_whatsapp = generar_qr(whatsapp_url)
        qr_img_email = generar_qr(email_url)
        qr_img_app = generar_qr(serie)

        # Fondo
        c.setFillColor(colors.white)
        c.rect(0, 0, WIDTH, HEIGHT, fill=1)

        # Borde azul
        c.setStrokeColor(colors.blue)
        c.setLineWidth(3)
        c.rect(10, 10, WIDTH - 20, HEIGHT - 20)

        # Logos
        try:
            c.drawImage(ImageReader(pbs_logo), 0.3 * inch, HEIGHT - 1.1 * inch, width=0.9 * inch, height=0.9 * inch, mask='auto')
            c.drawImage(ImageReader(xerox_logo), WIDTH - 1.2 * inch, HEIGHT - 1.1 * inch, width=0.9 * inch, height=0.9 * inch, mask='auto')
        except Exception as e:
            st.warning(f"⚠️ Error cargando logos: {e}")

        # Texto
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawString(100, HEIGHT - 30, f"Cliente: {cliente}")
        c.setFont("Helvetica", 9)
        c.drawString(100, HEIGHT - 45, f"Modelo: {modelo}")
        c.drawString(100, HEIGHT - 60, f"Serie: {serie}")

        # QRs
        qr_size = 80
        margin = 20
        gap = (WIDTH - 2 * margin - 3 * qr_size) / 2
        x1 = margin
        x2 = x1 + qr_size + gap
        x3 = x2 + qr_size + gap
        y_qr = HEIGHT - 150

        c.drawImage(qr_img_whatsapp, x1, y_qr, width=qr_size, height=qr_size)
        c.drawImage(qr_img_email, x2, y_qr, width=qr_size, height=qr_size)
        c.drawImage(qr_img_app, x3, y_qr, width=qr_size, height=qr_size)

        c.setFont("Helvetica", 8)
        c.drawCentredString(x1 + qr_size / 2, y_qr - 12, "WhatsApp")
        c.drawCentredString(x2 + qr_size / 2, y_qr - 12, "Email")
        c.drawCentredString(x3 + qr_size / 2, y_qr - 12, "App")

        # Contacto
        c.setFont("Helvetica", 7)
        c.drawString(100, 35, "Puede Contactarnos:")
        c.drawString(100, 25, "505 22552090")
        c.drawString(100, 15, "callcenter.ni@pbs.group")

        c.showPage()

    c.save()
    output.seek(0)

    st.success("✅ PDF generado correctamente")
    st.download_button("📥 Descargar etiquetas PDF", output, file_name="etiquetas_qr.pdf")

elif uploaded_file:
    st.warning("❗ Sube también los logos para continuar.")
