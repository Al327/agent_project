#!/usr/bin/env python3

from asterisk.agi import AGI

agi = AGI()


agi.verbose("Esperando un dígito DTMF...")
digito3=''
while True:
    try:
        digit = agi.wait_for_digit(timeout=40000)  # Espera 10 segundos para un dígito
        agi.verbose(f"Dígito recibido: {digit}")
        digito3 += digit  # Agregar el dígito a la cadena
        agi.verbose(f"Dígitos recibidos: {digit}")

        if digit == "#":
            agi.verbose("Carácter '#' ingresado. Terminando el bucle.")
            agi.verbose(f"Dígitos final: {digito3[:-1]}")
            agi.set_variable("recognition1", digito3[:-1])
        


            break  # Sale del bucle cuando se ingresa el carácter '#'
    except Exception as e:
        agi.verbose(f"Error en el canal: {e}")
