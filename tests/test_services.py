"""
Conjunto de testes para o módulo de serviços do sistema de gerenciamento de hotel.
"""

from hotel import services, config
from hotel.models import Adicional
from datetime import date, timedelta
import pytest


@pytest.fixture(autouse=True)
def setup_inicial():
    services.quartos_db.clear()
    services.hospedes_db.clear()
    services.reservas_db.clear()
    config.carregar_configuracoes()


# TESTES DE FUNÇÕES DE CADASTRO:

def test_cadastrar_quarto():
    services.cadastrar_quarto(101, "SIMPLES", 1, 100.0)
    quarto = services.buscar_quarto(101)
    assert quarto.numero == 101
    assert quarto.tipo == "SIMPLES"
    assert quarto.capacidade == 1
    assert quarto.tarifa_base == 100.0

def test_cadastrar_hospede():
    services.cadastrar_hospede("Jayr Alencar", "12345678900", "jayr.alencar@gmail.com", "(88) 12345-6789")
    hospede = services.buscar_hospede("12345678900")
    assert hospede.nome == "Jayr Alencar"
    assert hospede.documento == "12345678900"
    assert hospede.email == "jayr.alencar@gmail.com"
    assert hospede.telefone == "(88) 12345-6789"


# TESTES DE BUSCA: 

def test_buscar_quarto():
    services.cadastrar_quarto(101, "SIMPLES", 1, 100.0)
    quarto = services.buscar_quarto(101)
    assert quarto.numero == 101
    assert quarto.tipo == "SIMPLES"
    assert quarto.capacidade == 1
    assert quarto.tarifa_base == 100.0

def test_buscar_hospede():
    services.cadastrar_hospede("Jayr Alencar", "12345678900", "jayr.alencar@gmail.com", "(88) 12345-6789")
    hospede = services.buscar_hospede("12345678900")
    assert hospede.nome == "Jayr Alencar"
    assert hospede.documento == "12345678900"


# TESTES DE FUNÇÕES DE RESERVA:

def test_realizar_reserva():
    services.cadastrar_quarto(101, "SIMPLES", 1, 100.0)
    services.cadastrar_hospede("Jayr", "123", "e", "t")
    
    reserva = services.realizar_reserva("123", 101, date.today(), date.today() + timedelta(days=2), 1)
    
    assert reserva.hospede.documento == "123"
    assert reserva.quarto.numero == 101
    assert reserva.data_entrada == date.today()
    assert reserva.data_saida == date.today() + timedelta(days=2)
    assert reserva.status == "PENDENTE"

def test_cancelar_reserva():
    services.cadastrar_quarto(101, "SIMPLES", 1, 100.0)
    services.cadastrar_hospede("Jayr", "123", "e", "t")
    
    futuro = date.today() + timedelta(days=30)
    services.realizar_reserva("123", 101, futuro, futuro + timedelta(days=2), 1)
    
    services.cancelar_reserva("123", 101)
    r = services.buscar_reserva("123", 101)
    assert r.status == "CANCELADA"

def test_realizar_noshow():
    services.cadastrar_quarto(101, "SIMPLES", 1, 100.0)
    services.cadastrar_hospede("Jayr", "123", "e", "t")
    
    ontem = date.today() - timedelta(days=1)
    r = services.realizar_reserva("123", 101, ontem, date.today(), 1)
    r.confirmar()
    
    services.realizar_noshow("123", 101)
    
    assert r.status == "NO_SHOW"


# TESTES DE VALORES E TARIFAS:

def test_calcular_total_reserva():
    services.cadastrar_quarto(101, "SIMPLES", 1, 100.0)
    services.cadastrar_hospede("Jayr", "123", "e", "t")
    
    d1 = date(2025, 6, 10)
    d2 = date(2025, 6, 12)
    
    reserva = services.realizar_reserva("123", 101, d1, d2, 1)
    total = services.calcular_total_reserva(reserva)
    
    assert total == 220.0

def test_calcular_total_reserva_com_adicional():
    services.cadastrar_quarto(101, "SIMPLES", 1, 100.0)
    services.cadastrar_hospede("Jayr", "123", "e", "t")
    
    d1 = date(2025, 6, 10)
    d2 = date(2025, 6, 12)
    reserva = services.realizar_reserva("123", 101, d1, d2, 1)
    
    services.registrar_adicional("123", 101, "Pizza P Calabresa", 40.0)
    
    total = services.calcular_total_reserva(reserva)
    
    assert total == 264.0


# TESTES DE FLUXO DE ESTADIA:

def test_buscar_reserva():
    services.cadastrar_quarto(101, "SIMPLES", 1, 100.0)
    services.cadastrar_hospede("Jayr", "123", "e", "t")
    
    reserva = services.realizar_reserva("123", 101, date.today(), date.today() + timedelta(days=2), 1)
    encontrada = services.buscar_reserva("123", 101)
    assert encontrada == reserva

def test_realizar_checkin():
    services.cadastrar_quarto(101, "SIMPLES", 1, 100.0)
    services.cadastrar_hospede("Jayr", "123", "e", "t")
    
    r = services.realizar_reserva("123", 101, date.today(), date.today() + timedelta(days=2), 1)
    r.confirmar()
    
    services.realizar_checkin("123", 101)
    assert r.status == "CHECKIN"

def test_realizar_checkout():
    services.cadastrar_quarto(101, "SIMPLES", 1, 100.0)
    services.cadastrar_hospede("Jayr", "123", "e", "t")
    
    r = services.realizar_reserva("123", 101, date.today(), date.today() + timedelta(days=2), 1)
    r.confirmar()
    services.realizar_checkin("123", 101)
    
    total = services.calcular_total_reserva(r)
    services.registrar_pagamento("123", 101, total, "PIX")
    
    services.realizar_checkout("123", 101)
    assert r.status == "CHECKOUT"


# TESTES DE TRANSAÇÕES FINANCEIRAS:

def test_registrar_pagamento():
    services.cadastrar_quarto(101, "SIMPLES", 1, 100.0)
    services.cadastrar_hospede("Jayr", "123", "e", "t")
    
    reserva = services.realizar_reserva("123", 101, date.today(), date.today() + timedelta(days=2), 1)
    
    services.registrar_pagamento("123", 101, 200.0, "CARTAO")
    
    pagamento = reserva.pagamentos[0]
    assert pagamento.valor == 200.0
    assert pagamento.forma == "CARTAO"

def test_registrar_adicional():
    services.cadastrar_quarto(101, "SIMPLES", 1, 100.0)
    services.cadastrar_hospede("Jayr", "123", "e", "t")
    reserva = services.realizar_reserva("123", 101, date.today(), date.today() + timedelta(days=2), 1)
    
    services.registrar_adicional("123", 101, "Refrigerante Lata", 10.0)
    
    adicional = reserva.adicionais[0]
    assert adicional.descricao == "Refrigerante Lata"
    assert adicional.valor == 10.0


# TESTES DE PERSISTÊNCIA:

def test_inicializar_sistema():
    services.inicializar_sistema()
    assert isinstance(services.quartos_db, list)
    assert isinstance(services.hospedes_db, list)
    assert isinstance(services.reservas_db, list)

def test_salvar_tudo():
    services.cadastrar_quarto(101, "SIMPLES", 1, 100.0)
    services.salvar_tudo()
    assert True


# TESTES DE RELATÓRIOS E ESTATÍSTICAS:

def test_gerar_relatorio_ocupacao():
    services.cadastrar_quarto(101, "S", 1, 100.0)
    taxa = services.gerar_relatorio_ocupacao()
    assert taxa == 0.0

def test_gerar_relatorio_financeiro():
    services.cadastrar_quarto(101, "S", 1, 100.0)
    services.cadastrar_quarto(102, "S", 1, 100.0)
    services.cadastrar_hospede("Jayr", "123", "e", "t")
    
    r1 = services.realizar_reserva("123", 101, date(2025, 6, 10), date(2025, 6, 11), 1)
    r1.confirmar()
    r1.checkin()
    r1.checkout()
    
    r2 = services.realizar_reserva("123", 102, date(2025, 6, 10), date(2025, 6, 11), 1)
    r2.cancelar()
    
    metricas = services.gerar_relatorio_financeiro()
    
    assert metricas["receita"] == 110.0
    assert metricas["adr"] == 110.0
    assert metricas["revpar"] == 55.0
    assert metricas["cancelamento"] == 50.0


# TESTES DE CÁLCULO DE TARIFAS:

def test_verificar_temporada():
    hoje = date(2025, 12, 25) # Natal (alta temporada)
    assert services._verificar_temporada(hoje) == 1.5 
    
    hoje = date(2025, 3, 15) # Dia normal
    assert services._verificar_temporada(hoje) == 1.0

def test_calcular_valor_diaria():
    services.cadastrar_quarto(101, "SIMPLES", 1, 100.0)
    quarto = services.buscar_quarto(101) 
    
    hoje = date(2025, 12, 25)
    
    valor = services.calcular_valor_diaria(hoje, quarto.tarifa_base)
    
    assert valor == 150.0