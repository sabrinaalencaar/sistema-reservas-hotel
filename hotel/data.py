"""
Módulo responsável por salvar e carregar os dados do sistema em arquivos JSON.
"""

from hotel.models import Pessoa, Hospede, Quarto, QuartoLuxo, Pagamento, Adicional, Reserva
from datetime import datetime
from typing import List, Tuple
from time import sleep
from .config import Cores
import json
import os


# CONFIGURAÇÃO DOS ARQUIVOS

ARQUIVO_QUARTOS = "quartos.json"
ARQUIVO_HOSPEDES = "hospedes.json"
ARQUIVO_RESERVAS = "reservas.json"


# FUNÇÕES DE LEITURA E ESCRITA DE ARQUIVOS:

def _salvar_arquivo(caminho: str, dados: List[dict]):
    """
    Escreve uma lista de dicionários em um arquivo JSON.
    """
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar {caminho}: {e}")

def _carregar_arquivo(caminho: str) -> List[dict]:
    """
    Lê um arquivo JSON e retorna a lista de dicionários.
    """
    if not os.path.exists(caminho):
        return []
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler {caminho}: {e}")
        return []


# FUNÇÃO PARA SALVAR TUDO

def salvar_dados(quartos: List[Quarto], hospedes: List[Hospede], reservas: List[Reserva]):
    """
    Recebe as listas de objetos da memória e salva nos arquivos JSON.
    """
    quartos_dicts = [q.to_dict() for q in quartos]
    _salvar_arquivo(ARQUIVO_QUARTOS, quartos_dicts)

    hospedes_dicts = [h.to_dict() for h in hospedes]
    _salvar_arquivo(ARQUIVO_HOSPEDES, hospedes_dicts)

    reservas_dicts = [r.to_dict() for r in reservas]
    _salvar_arquivo(ARQUIVO_RESERVAS, reservas_dicts)

    print(f"{Cores.VERDE}Dados salvos com sucesso!{Cores.RESET}")


# FUNÇÃO PARA CARREGAR TUDO

def carregar_dados() -> Tuple[List[Quarto], List[Hospede], List[Reserva]]:
    """
    Lê os arquivos JSON, reconstrói os objetos e restaura os relacionamentos.
    """
    print("Carregando dados do disco...")
    sleep(3)

    dados_quartos = _carregar_arquivo(ARQUIVO_QUARTOS)
    lista_quartos = [Quarto.from_dict(d) for d in dados_quartos]

    dados_hospedes = _carregar_arquivo(ARQUIVO_HOSPEDES)
    lista_hospedes = [Hospede.from_dict(d) for d in dados_hospedes]

    dados_reservas = _carregar_arquivo(ARQUIVO_RESERVAS)
    lista_reservas = []

    for dado in dados_reservas:
        hospede_obj = next((h for h in lista_hospedes if h.documento == dado["hospede_documento"]), None)
        
        quarto_obj = next((q for q in lista_quartos if q.numero == dado["quarto_numero"]), None)

        if hospede_obj and quarto_obj:
            
            dt_entrada = datetime.fromisoformat(dado["data_entrada"]).date()
            dt_saida = datetime.fromisoformat(dado["data_saida"]).date()

            reserva = Reserva(
                hospede = hospede_obj,
                quarto = quarto_obj,
                data_entrada = dt_entrada,
                data_saida = dt_saida,
                num_hospedes = dado["num_hospedes"],
                status = dado["status"]
            )

            reserva.pagamentos = [Pagamento.from_dict(p) for p in dado["pagamentos"]]
            reserva.adicionais = [Adicional.from_dict(a) for a in dado["adicionais"]]

            hospede_obj.historico_reservas.append(reserva)
            
            lista_reservas.append(reserva)

    return lista_quartos, lista_hospedes, lista_reservas