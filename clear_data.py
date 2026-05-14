#!/usr/bin/env python
"""
Script para vaciar las tablas de articulos y simulaciones.
Uso: python clear_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from articulos.models import Articulo
from simulaciones.models import Simulacion

def clear_tables():
    print("=" * 70)
    print("VACIAR TABLAS DE ARTICULOS Y SIMULACIONES")
    print("=" * 70)
    
    # Contar registros antes
    articulos_count = Articulo.objects.count()
    simulaciones_count = Simulacion.objects.count()
    
    print(f"\nAntes:")
    print(f"  Articulos: {articulos_count}")
    print(f"  Simulaciones: {simulaciones_count}")
    
    # Confirmar
    respuesta = input("\nEsto eliminará TODOS los registros. ¿Continuar? (s/n): ").strip().lower()
    if respuesta != 's':
        print("Cancelado.")
        return
    
    # Vaciar tablas
    print("\nEliminando...")
    Simulacion.objects.all().delete()
    print(f"  Simulaciones eliminadas: {simulaciones_count}")
    
    Articulo.objects.all().delete()
    print(f"  Articulos eliminados: {articulos_count}")
    
    # Verificar
    print(f"\nDespues:")
    print(f"  Articulos: {Articulo.objects.count()}")
    print(f"  Simulaciones: {Simulacion.objects.count()}")
    print("\nListas vaciadas correctamente.")

if __name__ == '__main__':
    try:
        clear_tables()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
