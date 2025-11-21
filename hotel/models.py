"""
Armazena as definições de classe para o Sistema de Reservas de Hotel.
"""

from datetime import date, datetime
from typing import List

class Pessoa:
    """
    Classe base para representar uma pessoa com dados cadastrais.
    """
    def __init__(self, nome: str, documento: str, email: str, telefone: str):
        self.nome = nome
        self.documento = documento
        self.email = email
        self.telefone = telefone


class Hospede(Pessoa):
    """
    Representa um hóspede do hotel, herdando de Pessoa e contendo histórico de reservas.
    """
    def __init__(self, nome: str, documento: str, email: str, telefone: str):
        super().__init__(nome, documento, email, telefone)
        self.historico_reservas: List['Reserva'] = []


class Quarto:
    """
    Classe base que representa um quarto e define seus atributos e regras principais.
    """
    def __init__(self, numero: int, tipo: str, capacidade: int, tarifa_base: float, status: str):
        self.numero = numero
        self.tipo = tipo
        self.capacidade = capacidade
        self.tarifa_base = tarifa_base
        self.status = status

    def bloquear_quarto(self, data_inicio: date, data_fim: date, motivo: str):
        """
        Altera o status do quarto para MANUTENCAO por um período determinado.
        """
        pass

    def liberar_quarto(self):
        """
        Define o status do quarto como DISPONIVEL.
        """
        pass

    def __str__(self) -> str:
        """
        Retorna um resumo textual do quarto (ex: "Quarto 101 (LUXO)").
        """
        return f"Quarto {self.numero} ({self.tipo})"
    
    def __lt__(self, other: 'Quarto') -> bool:
        """
        Permite a ordenação de quartos, por tipo ou numeração.
        """
        pass


class QuartoLuxo(Quarto):
    """
    Subclasse de Quarto, representando um quarto tipo LUXO.
    Pode sobrescrever regras de tarifa.
    """
    pass


class Pagamento:
    """
    Representa um pagamento (parcial ou total) associado a uma Reserva.
    """
    def __init__(self, valor: float, forma: str, data: datetime = None):
        self.valor = valor
        self.forma = forma
        self.data = data or datetime.now()


class Adicional:
    """
    Representa um consumo extra (ex.: frigobar, estacionamento) lançado na Reserva.
    """
    def __init__(self, descricao: str, valor: float):
        self.descricao = descricao
        self.valor = valor


class Reserva:
    """
    Classe que gerencia as informações de reserva, conectando um Hóspede, um Quarto e um período de tempo.
    """
    def __init__(self, hospede: Hospede, quarto: Quarto, data_entrada: date, data_saida: date, num_hospedes: int, status: str):
        self.hospede = hospede
        self.quarto = quarto
        self.data_entrada = data_entrada
        self.data_saida = data_saida
        self.num_hospedes = num_hospedes
        self.status = status
        self.pagamentos: List['Pagamento'] = []
        self.adicionais: List['Adicional'] = []
    
    def confirmar(self):
        """
        Muda o status da reserva para CONFIRMADA.
        """
        pass

    def checkin(self):
        """
        Verifica se a data está correta e muda o status para CHECKIN.
        """
        pass

    def checkout(self):
        """
        Realiza o fechamento da conta e muda o status para CHECKOUT.
        """
        pass

    def cancelar(self):
        """
        Cancela a reserva e verifica regras de multa.
        """
        pass

    def calcular_total(self) -> float:
        """
        Calcula o valor total da reserva com base nas diárias, ajustes de temporada e adicionais.
        """
        pass

    def __len__(self) -> int:
        """
        Retorna o número de diárias (noites) da reserva.
        """
        pass

    def __eq__(self, other: 'Reserva') -> bool:
        """
        Verifica se duas reservas são idênticas (mesmo quarto e intervalo de datas que se sobrepõem).
        """
        pass