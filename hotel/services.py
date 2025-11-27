"""
Implementa as regras de negócio e operações principais do Sistema de Reservas de Hotel.
"""

from .models import Pessoa, Hospede, Quarto, QuartoLuxo, Pagamento, Adicional, Reserva
from datetime import datetime, date
from typing import List, Optional


# PERSISTÊNCIA TEMPORÁRIA EM MEMÓRIA: 

quartos_db: List[Quarto] = []
hospedes_db: List[Hospede] = []
reservas_db: List[Reserva] = []


# FUNCÕES DE BUSCA:

def buscar_quarto(numero: int) -> Optional[Quarto]:
    """
    Busca um quarto na lista pelo número.
    """
    for q in quartos_db:
        if q.numero == numero:
            return q
    return None

def buscar_hospede(documento: str) -> Optional[Hospede]:
    """
    Busca um hóspede na lista pelo documento.
    """
    for h in hospedes_db:
        if h.documento == documento:
            return h
    return None


# FUNÇÕES DE CADASTRO (CRUD):

def cadastrar_quarto(numero: int, tipo: str, capacidade: int, tarifa_base: float) -> Quarto:
    """
    Verifica se o quarto já existe e o cadastra se não existir.
    """
    if buscar_quarto(numero):
        raise ValueError(f"Erro: Já existe um quarto cadastrado com o número {numero}.")
    
    novo_quarto = Quarto(numero, tipo, capacidade, tarifa_base)
    
    quartos_db.append(novo_quarto)
    print(f"Quarto {numero} cadastrado com sucesso!")
    return novo_quarto

def cadastrar_hospede(nome: str, documento: str, email: str, telefone: str) -> Hospede:
    """
    Verifica se o hóspede já existe e o cadastra se não existir.
    """
    if buscar_hospede(documento):
        raise ValueError(f"Erro: Hóspede com documento {documento} já está cadastrado.")
        
    novo_hospede = Hospede(nome, documento, email, telefone)
    hospedes_db.append(novo_hospede)
    print(f"Hóspede {nome} cadastrado com sucesso!")
    return novo_hospede


# GESTÃO DE RESERVAS:

def realizar_reserva(doc_hospede: str, num_quarto: int, data_entrada: date, data_saida: date, num_hospedes: int) -> Reserva:
    """
    Tenta criar uma reserva vinculando um hóspede e um quarto.
    """
    hospede = buscar_hospede(doc_hospede)
    quarto = buscar_quarto(num_quarto)
    
    if not hospede:
        raise ValueError("Erro: Hóspede não encontrado. Cadastre-o antes.")
    if not quarto:
        raise ValueError("Erro: Quarto não encontrado.")
    
    if quarto.status != "DISPONIVEL":
        raise ValueError(f"Erro: O Quarto {num_quarto} não está disponível no momento (Status: {quarto.status}).")

    nova_reserva = Reserva(hospede, quarto, data_entrada, data_saida, num_hospedes)
    
    reservas_db.append(nova_reserva)
    hospede.historico_reservas.append(nova_reserva)
    
    print(f"Reserva criada com sucesso! {hospede.nome} vai ficar no Quarto {quarto.numero}.")
    return nova_reserva


# FLUXO DA ESTADIA (CHECK-IN / CHECK-OUT):

def buscar_reserva(hospede_doc: str, quarto_num: int) -> Optional[Reserva]:
    """
    Busca uma reserva ativa pelo documento do hóspede e número do quarto.
    """
    for r in reservas_db:
        if r.hospede.documento == hospede_doc and r.quarto.numero == quarto_num:
            return r
    return None

def realizar_checkin(doc_hospede: str, num_quarto: int):
    """
    Busca a reserva e tenta fazer o check-in.
    """
    reserva = buscar_reserva(doc_hospede, num_quarto)
    
    if not reserva:
        raise ValueError("Reserva não encontrada para este hóspede/quarto.")
    
    if reserva.checkin():
        print(f"Check-in realizado com sucesso para {reserva.hospede.nome}!")
    else:
        raise ValueError("Não foi possível realizar o check-in, verifique datas ou status.")

def realizar_checkout(doc_hospede: str, num_quarto: int):
    """
    Busca a reserva, calcula total e tenta fazer o check-out.
    """
    reserva = buscar_reserva(doc_hospede, num_quarto)
    
    if not reserva:
        raise ValueError("Reserva não encontrada para este hóspede/quarto.")
    
    total_conta = reserva.calcular_total()
    total_pago = sum(p.valor for p in reserva.pagamentos)
    
    if total_pago < total_conta:
        raise ValueError(f"Conta pendente! Total: R${total_conta}, Pago: R${total_pago}. Faltam R${total_conta - total_pago}")
    
    if reserva.checkout():
        print(f"Check-out realizado com sucesso! Quarto {num_quarto} liberado.")
    else:
        raise ValueError("Não foi possível realizar o check-out.")


# TRANSAÇÕES FINANCEIRAS:

def registrar_pagamento(doc_hospede: str, num_quarto: int, valor: float, forma: str):
    """
    Registra um pagamento para a reserva especificada.
    """
    reserva = buscar_reserva(doc_hospede, num_quarto)
    if not reserva:
        raise ValueError("Reserva não encontrada.")
        
    pagamento = Pagamento(valor, forma)
    reserva.pagamentos.append(pagamento)
    print(f"Pagamento no valor de R${valor} ({forma}) registrado com sucesso!")

def registrar_adicional(doc_hospede: str, num_quarto: int, descricao: str, valor: float):
    """
    Lança um consumo extra (frigobar, estacionamento) na conta da reserva.
    """
    reserva = buscar_reserva(doc_hospede, num_quarto)
    if not reserva:
        raise ValueError("Reserva não encontrada para este hóspede/quarto.")

    adicional = Adicional(descricao, valor)
    reserva.adicionais.append(adicional)
    print(f"Adicional '{descricao}' (R${valor}) adicionado à conta com sucesso!")