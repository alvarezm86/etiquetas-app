import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from urllib.parse import quote
import os

st.set_page_config(page_title="Generador de Etiquetas QR", layout="centered")
st.title("📦 Generador de Etiquetas con QR")

uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

# Logos desde el repositorio
pbs_logo_path = "pbs logo.jpg"
xerox_logo_path = "Xerox logo.jpg"

if uploaded_file:
    # Leer CSV
    try:
        df = pd.read_csv(uploaded_file, sep=';')
        st.success("✅ Archivo CSV cargado correctamente")
    except Exception as e:
        st.error(f"❌ Error al leer el archivo CSV: {e}")
        st.stop()

    # Mostrar vista previa del CSV
    st.subheader("🔍 Vista previa del archivo")
    st.dataframe(df.head(), use_container_width=True)

    # Comprobar columnas requeridas
    required_columns = {"Serie", "Modelo", "Nombre del Cliente"}
    if not required_columns.issubset(df.columns):
        st.error(f"❌ El CSV debe contener las columnas: {', '.join(required_columns)}")
        st.stop()

    WIDTH, HEIGHT = 4 * inch, 3 * inch
    output = BytesIO()
    c = canvas.Canvas(output, pagesize=(WIDTH, HEIGHT))

    for _, row in df.iterrows():
        serie = str(row["Serie"])
        modelo = str(row["Modelo"])
        cliente = str(row["Nombre del Cliente"])

        mensaje = f"Hola, soy de Nicaragua, me gustaria reportar mi equipo con serie {serie}, Modelo {modelo}, por la siguiente razón:"
        whatsapp_url = f"https://wa.me/50254566479?text={quote(mensaje)}"

        asunto = f"Equipo serie {serie}"
        cuerpo = mensaje
        email_url = f"mailto:servicio@grouppbs.com?subject={quote(asunto)}&body={quote(cuerpo)}"

        def generar_qr(data):
            qr = qrcode.make(data)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            buffer.seek(0)
            return ImageReader(buffer)

        qr_img_whatsapp = generar_qr(whatsapp_url)
        qr_img_email = generar_qr(email_url)
        qr_img_app = generar_qr(serie)

        # Fondo blanco y borde azul
        c.setFillColor(colors.white)
        c.rect(0, 0, WIDTH, HEIGHT, fill=1)
        c.setStrokeColor(colors.blue)
        c.setLineWidth(3)
        c.rect(10, 10, WIDTH - 20, HEIGHT - 20)

        # Logos
        try:
            c.drawImage(pbs_logo_path, 0.3 * inch, HEIGHT - 1.1 * inch, width=0.9 * inch, height=0.9 * inch, mask='auto')
        except:
            pass
        try:
            c.drawImage(xerox_logo_path, WIDTH - 1.2 * inch, HEIGHT - 1.1 * inch, width=0.9 * inch, height=0.9 * inch, mask='auto')
        except:
            pass

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
        c.drawString(100, 15, "servicio@grouppbs.com")

        c.showPage()

    c.save()
    output.seek(0)

    st.download_button("📥 Descargar etiquetas PDF", output, file_name="etiquetas_qr.pdf")
else:
    st.info("📄 Esperando que subas un archivo CSV para mostrar la previsualización y generar etiquetas.")

