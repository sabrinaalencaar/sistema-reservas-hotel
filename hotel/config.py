"""
Módulo para carregar as configurações do arquivo settings.json.
"""

import json
import os
from typing import List, Dict

ARQUIVO_SETTINGS = "settings.json"

regras = {}

def carregar_configuracoes():
    """
    Lê o arquivo settings.json e carrega as regras para a memória.
    """
    global regras
    if not os.path.exists(ARQUIVO_SETTINGS):
        print(f"Aviso: {ARQUIVO_SETTINGS} não encontrado.")
        return

    try:
        with open(ARQUIVO_SETTINGS, "r", encoding="utf-8") as f:
            regras = json.load(f)
            print("Configurações carregadas com sucesso!")
    except Exception as e:
        print(f"Erro ao ler configurações: {e}")


# GETTERS HOTEL

def get_info_hotel() -> Dict:
    """
    Retorna as informações básicas do hotel.
    """
    return regras.get("hotel", {})

def get_horarios():
    """
    Retorna o dicionário de horários (checkin, checkout, tolerancia).
    """
    return regras.get("hotel", {}).get("horarios", {})


# GETTERS FINANCEIRO

def get_taxa_servico() -> float:
    """
    Retorna a taxa de serviço.
    """
    return regras.get("financeiro", {}).get("taxa_servico", 0.0)

def get_multiplicador_fim_de_semana() -> float:
    """
    Retorna o multiplicador de fim de semana.
    """
    return regras.get("financeiro", {}).get("multiplicador_fim_de_semana", 1.0)


# GETTERS POLÍTICA DE CANCELAMENTO

def get_politica_cancelamento() -> dict:
    """
    Retorna o dicionário de política de cancelamento.
    """
    return regras.get("politica_cancelamento", {
        "multa_padrao": 0.20,
        "multa_noshow": 1.0,
        "horas_limite_sem_multa": 24
    })

def get_multa_padrao() -> float:
    """
    Retorna a multa padrão de cancelamento.
    """
    return regras.get("politica_cancelamento", {}).get("multa_padrao", 0.0)

def get_multa_noshow() -> float:
    """
    Retorna a multa de no-show.
    """
    return regras.get("politica_cancelamento", {}).get("multa_noshow", 1.0)


# GETTERS TEMPORADAS

def get_temporadas() -> List[Dict]:
    """
    Retorna a lista de temporadas configuradas.
    """
    return regras.get("temporadas", [])