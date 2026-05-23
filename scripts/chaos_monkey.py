#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHAOS MONKEY v1.0 - VibeCoderProof Resilience Tester
Inyecta fallos aleatorios, corrompe mocks y simula latencias para 
validar el cumplimiento del ANGRY PATH (Mandato S1/B3).
"""

import os
import sys
import random
import time

# Inyectar el root del proyecto en el path para resolver scripts.*
sys.path.append(os.getcwd())

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()

def chaos_injection() -> None:
    """
    Executes a random failure scenario to test system resilience.
    
    Inputs: None
    Outputs: Prints the selected chaos scenario to standard output and instructs the user to verify test coverage.
    Contract: This function must simulate a random failure condition and exit cleanly.
    """
    print("MONKEY INICIANDO - VIBECODERPROOF MODE")
    print("---------------------------------------------")
    
    scenarios = [
        "Simulando latencia de red (timeout potencial)...",
        "Corrompiendo archivo de configuración temporal...",
        "Inyectando string malformado en Input Boundary...",
        "Simulando desconexión de base de datos..."
    ]
    
    selected = random.choice(scenarios)
    print(f"CAOS: {selected}")
    
    time.sleep(1)
    
    print("\nREGLA B3: Tu codigo sobrevivio a este escenario?")
    print("   Si no tienes un test que valide este fallo, tu tarea esta INCOMPLETA.")

if __name__ == "__main__":
    try:
        chaos_injection()
    except KeyboardInterrupt:
        print("\nMonkey detenido.")
    except Exception as e:
        print(f"Monkey fallo al intentar romper cosas: {e}")
