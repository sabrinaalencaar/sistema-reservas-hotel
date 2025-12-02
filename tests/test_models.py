"""
Conjunto de testes para verificação de comportamento, encapsulamento e lógica das classes.
"""

from hotel.models import Pessoa, Hospede, Quarto, QuartoLuxo, Pagamento, Adicional, Reserva
from datetime import date, timedelta
import pytest


# TESTES DE PESSOA E HÓSPEDE:

def test_criar_pessoa():
    pessoa = Pessoa("Jayr Alencar", "12345678900", "jayr.alencar@gmail.com", "(88) 12345-6789")
    assert pessoa.nome == "Jayr Alencar"
    assert pessoa.documento == "12345678900"
    assert pessoa.email == "jayr.alencar@gmail.com"
    assert pessoa.telefone == "(88) 12345-6789"

def test_historico_reservas_hospede():
    hospede = Hospede("Jayr Alencar", "12345678900", "jayr.alencar@gmail.com", "(88) 12345-6789")
    assert hospede.historico_reservas == []


# TESTES DE QUARTO E QUARTO DE LUXO:

def test_quarto_valido():
    quarto = Quarto(101, "SIMPLES", 1, 100.0, "DISPONIVEL")

    assert quarto.numero == 101
    assert quarto.tipo == "SIMPLES"
    assert quarto.capacidade == 1
    assert quarto.tarifa_base == 100.0
    assert quarto.status == "DISPONIVEL"

def test_quarto_capacidade_invalida():
    with pytest.raises(ValueError):
        Quarto(102, "SIMPLES", 0, 150.0, "DISPONIVEL")

def test_quarto_tarifa_invalida():
    with pytest.raises(ValueError):
        Quarto(201, "DUPLO", 2, -50.0, "DISPONIVEL")

def test_quarto_bloquear_liberar():
    quarto = Quarto(303, "DUPLO", 3, 200.0, "DISPONIVEL")
    
    quarto.bloquear_quarto(date(2025, 12, 1), date(2025, 12, 10), "Reforma")
    assert quarto.status == "MANUTENCAO"
    
    quarto.liberar_quarto()
    assert quarto.status == "DISPONIVEL"

def test_quarto_str():
    quarto = Quarto(202, "DUPLO", 2, 150.0, "DISPONIVEL")
    assert str(quarto) == "Quarto 202 (DUPLO)"

def test_quarto_lt():
    quarto1 = Quarto(101, "SIMPLES", 1, 100.0, "DISPONIVEL")
    quarto2 = Quarto(102, "DUPLO", 2, 150.0, "DISPONIVEL")
    assert quarto1 < quarto2

def test_quarto_luxo_tarifa():
    quarto_luxo = QuartoLuxo(401, 200.0, "DISPONIVEL")

    assert quarto_luxo.numero == 401
    assert quarto_luxo.tipo == "LUXO"
    assert quarto_luxo.capacidade == 4
    assert quarto_luxo.tarifa_base == 300.0


# TESTES DE PAGAMENTO E ADICIONAL:

def test_pagamento_valido():
    pagamento = Pagamento(250.0, "CARTAO")
    assert pagamento.valor == 250.0
    assert pagamento.forma == "CARTAO"

def test_pagamento_valor_invalido():
    with pytest.raises(ValueError):
        Pagamento(-100.0, "DINHEIRO")

def test_adicional_valido():
    adicional = Adicional("Pizza P Calabresa", 40.0)
    assert adicional.descricao == "Pizza P Calabresa"
    assert adicional.valor == 40.0

def test_adicional_valor_invalido():
    with pytest.raises(ValueError):
        Adicional("Refrigerante Lata", 0.0)


# TESTES DE RESERVA:

def test_reserva_valida():
    hospede = Hospede("Jayr Alencar", "12345678900", "jayr.alencar@gmail.com", "(88) 12345-6789")
    quarto = Quarto(101, "SIMPLES", 2, 100.0, "DISPONIVEL")
    data_entrada = date(2025, 12, 1)
    data_saida = date(2025, 12, 5)
    num_hospedes = 1
    reserva = Reserva(hospede, quarto, data_entrada, data_saida, num_hospedes)
    assert reserva.hospede.nome == "Jayr Alencar"
    assert reserva.quarto.numero == 101
    assert reserva.status == "PENDENTE"
    assert len(reserva) == 4

def test_reserva_data_saida_invalida():
    hospede = Hospede("Jayr Alencar", "12345678900", "jayr.alencar@gmail.com", "(88) 12345-6789")
    quarto = Quarto(101, "SIMPLES", 2, 100.0, "DISPONIVEL")
    data_entrada = date(2025, 12, 5)
    data_saida = date(2025, 12, 1)
    num_hospedes = 1
    with pytest.raises(ValueError):
        Reserva(hospede, quarto, data_entrada, data_saida, num_hospedes)

def test_reserva_num_hospedes_excedente():
    hospede = Hospede("Jayr Alencar", "12345678900", "jayr.alencar@gmail.com", "(88) 12345-6789")
    quarto = Quarto(101, "SIMPLES", 2, 100.0, "DISPONIVEL")
    data_entrada = date(2025, 12, 1)
    data_saida = date(2025, 12, 5)
    num_hospedes = 3
    with pytest.raises(ValueError):
        Reserva(hospede, quarto, data_entrada, data_saida, num_hospedes)

def test_reserva_confirmar_cancelar():
    hospede = Hospede("Jayr Alencar", "12345678900", "jayr.alencar@gmail.com", "(88) 12345-6789")
    quarto = Quarto(101, "SIMPLES", 2, 100.0, "DISPONIVEL")
    data_entrada = date(2025, 12, 1)
    data_saida = date(2025, 12, 5)
    num_hospedes = 1
    reserva = Reserva(hospede, quarto, data_entrada, data_saida, num_hospedes)
    assert reserva.confirmar() is True
    assert reserva.status == "CONFIRMADA"
    assert reserva.cancelar() is True
    assert reserva.status == "CANCELADA"
    assert reserva.quarto.status == "DISPONIVEL"

def test_reserva_checkin_checkout():
    hospede = Hospede("Jayr Alencar", "12345678900", "jayr.alencar@gmail.com", "(88) 12345-6789")
    quarto = Quarto(101, "SIMPLES", 2, 100.0, "DISPONIVEL")
    data_entrada = date.today()
    data_saida = data_entrada + timedelta(days=3)
    num_hospedes = 1
    reserva = Reserva(hospede, quarto, data_entrada, data_saida, num_hospedes)
    assert reserva.confirmar() is True
    assert reserva.checkin() is True
    assert reserva.status == "CHECKIN"
    assert reserva.quarto.status == "OCUPADO"
    assert reserva.checkout() is True
    assert reserva.status == "CHECKOUT"
    assert reserva.quarto.status == "DISPONIVEL"

def test_reserva_calcular_total():
    hospede = Hospede("Jayr Alencar", "12345678900", "jayr.alencar@gmail.com", "(88) 12345-6789")
    quarto = Quarto(101, "SIMPLES", 2, 100.0, "DISPONIVEL")
    data_entrada = date(2025, 12, 1)
    data_saida = date(2025, 12, 5)
    num_hospedes = 1
    reserva = Reserva(hospede, quarto, data_entrada, data_saida, num_hospedes)
    adicional1 = Adicional("Pizza P Calabresa", 40.0)
    adicional2 = Adicional("Refrigerante Lata", 10.0)
    reserva.adicionais.append(adicional1)
    reserva.adicionais.append(adicional2)
    total = reserva.calcular_total()
    assert total == 450.0

def test_reserva_len():
    hospede = Hospede("Jayr Alencar", "12345678900", "jayr.alencar@gmail.com", "(88) 12345-6789")
    quarto = Quarto(101, "SIMPLES", 2, 100.0, "DISPONIVEL")
    data_entrada = date(2025, 12, 1)
    data_saida = date(2025, 12, 5)
    num_hospedes = 1
    reserva = Reserva(hospede, quarto, data_entrada, data_saida, num_hospedes)
    assert len(reserva) == 4

def test_reserva_eq():
    hospede = Hospede("Jayr Alencar", "12345678900", "jayr.alencar@gmail.com", "(88) 12345-6789")
    quarto = Quarto(101, "SIMPLES", 2, 100.0, "DISPONIVEL")
    data_entrada = date(2025, 12, 1)
    data_saida = date(2025, 12, 5)
    num_hospedes = 1
    reserva = Reserva(hospede, quarto, data_entrada, data_saida, num_hospedes)
    reserva_igual = Reserva(hospede, quarto, data_entrada, data_saida, num_hospedes)
    assert reserva == reserva_igual
    reserva_diferente = Reserva(hospede, quarto, date(2025, 12, 2), data_saida, num_hospedes)
    assert reserva != reserva_diferente