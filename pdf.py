from fpdf import FPDF

 ## P: portrait (vertical)
 ## L: landscape (horizontal)
 ## A4: 210*297mm

#orientacion y tamaño de la pagina
pdf = FPDF(orientation= "L", unit= "mm", format="A4")
pdf.add_page()


#texto 
pdf.set_font("arial","",18)
pdf.cell(0,10,"Empresa Electrica Poseidon Energy", ln=1, align="c" )

#imagen (jpg/png)
pdf.image("imagen1.png", x=50, y=50, 
          w=60, h=60)

pdf.output("hoja.pdf")