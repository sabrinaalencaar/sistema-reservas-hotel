"""
Módulo de inicialização rápida do sistema.
"""

from hotel.main import main


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSaindo...")