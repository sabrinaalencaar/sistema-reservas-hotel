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

    def to_dict(self):
        """
        Converte os dados cadastrais do hóspede para dicionário.
        """
        return {
            "nome": self.nome,
            "documento": self.documento,
            "email": self.email,
            "telefone": self.telefone
        }

    @classmethod
    def from_dict(cls, dados):
        """
        Cria um objeto Hospede a partir dos dados salvos.
        """
        return cls(
            nome = dados["nome"],
            documento = dados["documento"],
            email = dados["email"],
            telefone = dados["telefone"]
        )


class Quarto:
    """
    Classe base que representa um quarto e define seus atributos e regras principais.
    """
    def __init__(self, numero: int, tipo: str, capacidade: int, tarifa_base: float, status: str = "DISPONIVEL"):
        self.numero = numero
        self.tipo = tipo
        self.status = status
        self.definir_capacidade(capacidade)
        self.definir_tarifa(tarifa_base)

    def definir_capacidade(self, capacidade: int):
        """
        Validação: Deve ser um valor positivo.
        """
        if capacidade <= 0:
            raise ValueError("A capacidade deve ser maior que zero.")
        else:
            self.capacidade = capacidade

    def definir_tarifa(self, tarifa_base: float):
        """
        Validação: Deve ser um valor positivo.
        """
        if tarifa_base <= 0:
            raise ValueError("A tarifa base deve ser maior que zero.")
        else:
            self.tarifa_base = tarifa_base

    def bloquear_quarto(self, data_inicio: date, data_fim: date, motivo: str):
        """
        Altera o status do quarto para MANUTENCAO por um período determinado.
        """
        self.status = "MANUTENCAO"

    def liberar_quarto(self):
        """
        Define o status do quarto como DISPONIVEL.
        """
        self.status = "DISPONIVEL"

    def __str__(self) -> str:
        """
        Retorna um resumo textual do quarto (ex: "Quarto 101 (LUXO)").
        """
        return f"Quarto {self.numero} ({self.tipo})"
    
    def __lt__(self, other: 'Quarto') -> bool:
        """
        Permite a ordenação de quartos, por tipo ou numeração.
        """
        return self.numero < other.numero

    def to_dict(self):
        """
        Converte os dados do quarto para um dicionário.
        """
        return {
            "numero": self.numero,
            "tipo": self.tipo,
            "capacidade": self.capacidade,
            "tarifa_base": self.tarifa_base,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, dados):
        """
        Cria um objeto Quarto a partir dos dados salvos.
        """
        return cls(
            numero = dados["numero"],
            tipo = dados["tipo"],
            capacidade = dados["capacidade"],
            tarifa_base = dados["tarifa_base"],
            status = dados["status"]
        )


class QuartoLuxo(Quarto):
    """
    Subclasse de Quarto, representando um quarto tipo LUXO.
    Pode sobrescrever regras de tarifa.
    """
    def __init__(self, numero: int, tarifa_base: float, status: str = "DISPONIVEL"):
        tarifa_luxo = tarifa_base * 1.5
        super().__init__(numero, "LUXO", 4, tarifa_luxo, status)


class Pagamento:
    """
    Representa um pagamento (parcial ou total) associado a uma Reserva.
    """
    def __init__(self, valor: float, forma: str, data: datetime = None):
        self.definir_valor(valor)
        self.forma = forma
        self.data = data or datetime.now()

    def definir_valor(self, valor: float):
        """
        Validação: Deve ser um valor positivo.
        """
        if valor <= 0:
            raise ValueError("O valor do pagamento deve ser maior que zero.")
        else:
            self.valor = valor

    def to_dict(self):
        """
        Converte o pagamento para dicionário, transformando a data em texto.
        """
        return {
            "valor": self.valor,
            "forma": self.forma,
            "data": self.data.isoformat() # Converte data para texto
        }

    @classmethod
    def from_dict(cls, dados):
        """
        Recupera o pagamento, convertendo o texto da data de volta para datetime.
        """
        return cls(
            valor = dados["valor"],
            forma = dados["forma"],
            data = datetime.fromisoformat(dados["data"]) # Converte texto para data
        )


class Adicional:
    """
    Representa um consumo extra (ex.: frigobar, estacionamento) lançado na Reserva.
    """
    def __init__(self, descricao: str, valor: float):
        self.descricao = descricao
        self.definir_valor(valor)

    def definir_valor(self, valor: float):
        """
        Validação: Deve ser um valor positivo.
        """
        if valor <= 0:
            raise ValueError("O valor do adicional deve ser maior que zero.")
        else:
            self.valor = valor

    def to_dict(self):
        """
        Converte o item adicional para um dicionário simples.
        """
        return {
            "descricao": self.descricao,
            "valor": self.valor
        }

    @classmethod
    def from_dict(cls, dados):
        """
        Reconstroi o objeto Adicional a partir dos dados do dicionário.
        """
        return cls(
            descricao = dados["descricao"],
            valor = dados["valor"]
        )


class Reserva:
    """
    Classe que gerencia as informações de reserva, conectando um Hóspede, um Quarto e um período de tempo.
    """
    def __init__(self, hospede: Hospede, quarto: Quarto, data_entrada: date, data_saida: date, num_hospedes: int, status: str = "PENDENTE"):
        self.hospede = hospede
        self.quarto = quarto
        self.data_entrada = data_entrada
        self.definir_data_saida(data_saida)
        self.definir_num_hospedes(num_hospedes)
        self.status = status
        self.pagamentos: List['Pagamento'] = []
        self.adicionais: List['Adicional'] = []
    
    def definir_data_saida(self, data_saida: date):
        """
        Validação: Deve ser posterior à data de entrada.
        """
        if data_saida < self.data_entrada:
            raise ValueError("A data de saída deve ser posterior à data de entrada.")
        else:
            self.data_saida = data_saida
    
    def definir_num_hospedes(self, num_hospedes: int):
        """
        Validação: Deve ser um valor positivo e não exceder a capacidade do quarto.
        """
        if num_hospedes <= 0:
            raise ValueError("O número de hóspedes deve ser maior que zero.")
        elif num_hospedes > self.quarto.capacidade:
            raise ValueError("O número de hóspedes excede a capacidade do quarto.")
        else:
            self.num_hospedes = num_hospedes
    
    def confirmar(self):
        """
        Muda o status da reserva para CONFIRMADA.
        """
        if self.status == "PENDENTE":
            self.status = "CONFIRMADA"
            return True
        else: 
            return False

    def checkin(self):
        """
        Verifica se a data está correta e muda o status para CHECKIN.
        """
        if self.status == "CONFIRMADA" and date.today() >= self.data_entrada and date.today() <= self.data_saida:
            self.status = "CHECKIN"
            self.quarto.status = "OCUPADO"
            return True
        else: 
            return False

    def checkout(self):
        """
        Realiza o fechamento da conta e muda o status para CHECKOUT.
        """
        if self.status == "CHECKIN":
            self.status = "CHECKOUT"
            self.quarto.liberar_quarto()
            return True
        else: 
            return False

    def cancelar(self):
        """
        Cancela a reserva e verifica regras de multa.
        """
        if self.status in ["PENDENTE", "CONFIRMADA"]:
            self.status = "CANCELADA"
            self.quarto.liberar_quarto()
            return True
        else: 
            return False

    def calcular_total(self) -> float:
        """
        Calcula o valor total da reserva com base nas diárias, ajustes de temporada e adicionais.
        """
        total_diarias = self.quarto.tarifa_base * len(self)
        total_adicionais = sum(adicional.valor for adicional in self.adicionais)
        return total_diarias + total_adicionais

    def __len__(self) -> int:
        """
        Retorna o número de diárias da reserva.
        """
        delta = self.data_saida - self.data_entrada
        return delta.days

    def __eq__(self, other: 'Reserva') -> bool:
        """
        Verifica se duas reservas são idênticas (mesmo quarto e intervalo de datas que se sobrepõem).
        """
        if not isinstance(other, Reserva):
            return False
        return (self.quarto.numero == other.quarto.numero and
                self.data_entrada == other.data_entrada and
                self.data_saida == other.data_saida)
    
    def to_dict(self):
        """
        Converte a reserva em dicionário, salvando apenas os identificadores (IDs) do hóspede e do quarto, e convertendo datas para texto.
        """
        return {
            "hospede_documento": self.hospede.documento,
            "quarto_numero": self.quarto.numero,
            "data_entrada": self.data_entrada.isoformat(),
            "data_saida": self.data_saida.isoformat(),
            "num_hospedes": self.num_hospedes,
            "status": self.status,
            "pagamentos": [p.to_dict() for p in self.pagamentos],
            "adicionais": [a.to_dict() for a in self.adicionais]
        }