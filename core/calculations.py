"""
Sistema de cálculos da Calculadora PAP.

Este módulo contém as classes responsáveis pelos cálculos dos componentes do PAP.
"""

from typing import Dict, List, Tuple
import pandas as pd
from .models import ServiceSelection, CalculationResults, ConfigManager
from utils.formatting import format_currency # CORRIGIDO: Import absoluto


class PAPCalculator:
    """Calculadora principal do PAP."""
    
    def __init__(self):
        self.config = ConfigManager() 
    
    def calculate_fixed_component(self, service_selection: ServiceSelection, ied: str) -> Tuple[float, List[List]]:
        """Calcula o componente fixo do PAP (apenas custeio de eSF, eAP, eMulti)."""
        fixed_table = []
        total_value = 0
        
        estrato = self._get_estrato(ied)
        
        fixed_services = ["eSF", "eAP 30h", "eAP 20h", "eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]
        
        for service in fixed_services:
            quantity = service_selection.services.get(service, 0)
            if quantity > 0:
                valor = self._get_service_fixed_value(service, estrato, service_selection.edited_values)
                service_total = valor * quantity
                total_value += service_total
                
                fixed_table.append([
                    service, 
                    format_currency(valor), 
                    quantity, 
                    format_currency(service_total)
                ])
        
        # A implantação de eSF/eAP/eMulti foi movida para um componente separado.
        return total_value, fixed_table
    
    def calculate_core_implantacao_component(self, service_selection: ServiceSelection) -> Tuple[float, List[List]]:
        """Calcula o componente de implantação para eSF, eAP e eMulti."""
        # Este método agora é um wrapper direto para _calculate_implantacao_rows
        # que lida especificamente com a implantação desses serviços principais.
        total_implantacao_geral, implantacao_rows = self._calculate_implantacao_rows(service_selection)
        return total_implantacao_geral, implantacao_rows

    def calculate_vinculo_component(self, service_selection: ServiceSelection, vinculo: str) -> Tuple[float, List[List]]:
        """Calcula o componente de vínculo e acompanhamento territorial."""
        vinculo_table = []
        total_value = 0
        
        # Usar VINCULO_VALUES do ConfigManager
        vinculo_values_config = self.config.get_vinculo_values()
        
        for service, quality_levels in vinculo_values_config.items():
            if vinculo in quality_levels:
                quantity = service_selection.services.get(service, 0)
                if quantity > 0:
                    # Usar valor editado se disponível
                    if service in service_selection.edited_values:
                        # Assume que edited_values armazena o valor numérico float
                        value = service_selection.edited_values[service]
                    else:
                        value = quality_levels[vinculo]
                    
                    service_total = value * quantity
                    total_value += service_total
                    
                    vinculo_table.append([
                        service, 
                        vinculo, 
                        format_currency(value), 
                        quantity, 
                        format_currency(service_total)
                    ])
        
        return total_value, vinculo_table
    
    def calculate_quality_component(self, service_selection: ServiceSelection, classificacao: str) -> Tuple[float, List[List]]:
        """Calcula o componente de qualidade."""
        quality_table = []
        total_value = 0
        
        # quality_values já é carregado pelo ConfigManager
        for service, quality_levels in self.config.quality_values.items():
            if classificacao in quality_levels:
                quantity = service_selection.services.get(service, 0)
                if quantity > 0:
                    # Usar valor editado se disponível
                    if service in service_selection.edited_values:
                        value = service_selection.edited_values[service]
                    else:
                        value = quality_levels[classificacao] # Assume que isso já é float
                    
                    service_total = value * quantity
                    total_value += service_total
                    
                    quality_table.append([
                        service, 
                        classificacao, 
                        format_currency(value), 
                        quantity, 
                        format_currency(service_total)
                    ])
        
        return total_value, quality_table
    
    def calculate_outros_programas_component(self, service_selection: ServiceSelection) -> Tuple[float, List[List]]: # RENOMEADO
        """Calcula o componente de implantação e manutenção de OUTROS programas, serviços, etc."""
        outros_programas_table = [] # RENOMEADO
        total_value = 0
        
        saude_bucal_services = self.config.updated_categories.get('Saúde Bucal', [])
        servicos_pap_principais = ["eSF", "eAP 30h", "eAP 20h", "eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]
        
        for service, service_data_config in self.config.data.items():
            if (service not in self.config.quality_values and
                service_data_config.get('valor') != 'Sem cálculo' and
                service not in saude_bucal_services and
                service not in servicos_pap_principais):
                
                quantity = service_selection.services.get(service, 0)
                if quantity > 0:
                    valor = self._get_service_value_from_config(service, service_selection.edited_values)
                    service_total = valor * quantity
                    total_value += service_total
                    
                    outros_programas_table.append([ # RENOMEADO
                        service, 
                        quantity, 
                        format_currency(valor), 
                        format_currency(service_total)
                    ])
        
        return total_value, outros_programas_table # RENOMEADO

    def calculate_saude_bucal_component(self, service_selection: ServiceSelection) -> Tuple[float, List[List]]:
        """Calcula o componente de saúde bucal.
        Baseado na lógica de `calculations.py` (raiz), que usa `data[service]['valor']` e depois `edited_values`.
        Não usa `quality_values` para Saúde Bucal, diferente da implementação anterior em `core/calculations.py`.
        """
        saude_bucal_table = []
        total_value = 0
        
        saude_bucal_services = self.config.updated_categories.get('Saúde Bucal', [])
        
        for service in saude_bucal_services:
            quantity = service_selection.services.get(service, 0)
            if quantity > 0:
                # Usar valor editado se disponível, senão o valor de config.json['data']
                if service in service_selection.edited_values:
                    valor = service_selection.edited_values[service] # Assume float
                else:
                    service_info = self.config.get_service_info(service)
                    valor_str = service_info.get('valor')
                    if valor_str == 'Sem cálculo' or valor_str is None:
                        valor = 0.0
                    else:
                        valor = self._parse_currency_string(valor_str)
                
                service_total = valor * quantity
                total_value += service_total
                
                saude_bucal_table.append([
                    service, 
                    quantity, 
                    format_currency(valor), 
                    format_currency(service_total)
                ])
        
        return total_value, saude_bucal_table

    def calculate_per_capita_component(self, populacao: int) -> Tuple[float, List[List]]:
        """Calcula o componente per capita."""
        # Valor per capita conforme calculations.py (raiz)
        valor_per_capita_anual_base = 5.95 
        # O cálculo em calculations.py (raiz) divide por 12, então o valor base é anual.
        # Para consistência, vamos manter o cálculo mensal aqui.
        total_per_capita_mensal = (valor_per_capita_anual_base * populacao) / 12
        
        per_capita_table_data = [
            ['Valor per capita (anual por habitante)', format_currency(valor_per_capita_anual_base), '', ''],
            ['População Considerada', populacao, '', ''],
            ['Total Per Capita (Mensal)', '', '', format_currency(total_per_capita_mensal)]
        ]
        
        return total_per_capita_mensal, per_capita_table_data

    def calculate_all_components(self, service_selection: ServiceSelection, 
                               classificacao: str, vinculo: str, ied: str, 
                               populacao: int = 0,
                               ) -> CalculationResults:
        """Calcula todos os componentes do PAP."""
        
        results = CalculationResults()
        
        results.total_fixed_value, results.fixed_table = self.calculate_fixed_component(
            service_selection, ied
        )
        
        results.total_vinculo_value, results.vinculo_table = self.calculate_vinculo_component(
            service_selection, vinculo
        )
        
        results.total_quality_value, results.quality_table = self.calculate_quality_component(
            service_selection, classificacao
        )

        # NOVO: Componente de Implantação (eSF, eAP, eMulti)
        results.total_core_implantacao_value, results.core_implantacao_table = self.calculate_core_implantacao_component(
            service_selection
        )
        
        # RENOMEADO: Componente de Outros Programas (antigo Implantação e Manutenção)
        results.total_outros_programas_value, results.outros_programas_table = self.calculate_outros_programas_component(
            service_selection
        )
        
        results.total_saude_bucal_value, results.saude_bucal_table = self.calculate_saude_bucal_component(
            service_selection
        )
        
        results.total_per_capita, results.per_capita_table = self.calculate_per_capita_component(populacao)
        
        results.calculate_total_geral()
        
        results.total_incentivo_aps_esf_eap = 0
        for row in results.fixed_table:
            service_name = row[0]
            if service_name in ["eSF", "eAP 30h", "eAP 20h"]:
                results.total_incentivo_aps_esf_eap += self._parse_currency_string(row[3])
        
        # Adicionar implantação de eSF/eAP ao subtotal
        for row in results.core_implantacao_table:
            service_name = row[0] # Ex: "eSF (Implantação)"
            if any(s in service_name for s in ["eSF", "eAP 30h", "eAP 20h"]):
                 results.total_incentivo_aps_esf_eap += self._parse_currency_string(row[3])

        for row in results.quality_table:
            service_name = row[0]
            if service_name in ["eSF", "eAP 30h", "eAP 20h"]:
                results.total_incentivo_aps_esf_eap += self._parse_currency_string(row[4])
        
        for row in results.vinculo_table:
            service_name = row[0]
            if service_name in ["eSF", "eAP 30h", "eAP 20h"]:
                results.total_incentivo_aps_esf_eap += self._parse_currency_string(row[4])

        results.total_incentivo_aps_emulti = 0
        for row in results.fixed_table:
            service_name = row[0]
            if service_name in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
                results.total_incentivo_aps_emulti += self._parse_currency_string(row[3])

        # Adicionar implantação de eMulti ao subtotal
        for row in results.core_implantacao_table:
            service_name = row[0] # Ex: "eMULTI Ampl. (Implantação)"
            if any(s in service_name for s in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]):
                results.total_incentivo_aps_emulti += self._parse_currency_string(row[3])

        for row in results.quality_table:
            service_name = row[0]
            if service_name in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
                results.total_incentivo_aps_emulti += self._parse_currency_string(row[4])
        
        return results

    def _get_estrato(self, ied: str) -> str:
        """Extrai o estrato do IED."""
        if ied and isinstance(ied, str) and ied.startswith("ESTRATO "):
            try:
                return ied[-1]
            except IndexError:
                raise ValueError(f"Erro ao extrair estrato do IED: {ied}")
        
        raise ValueError("IED ausente ou inválido. Não é possível determinar o estrato.")
    
    def _get_service_fixed_value(self, service: str, estrato: str, edited_values: Dict[str, float]) -> float:
        """Obtém o valor de um serviço do componente fixo, considerando valores editados."""
        if service in edited_values:
            return edited_values[service] # Assume que já é float
        
        if service in ["eSF", "eAP 30h", "eAP 20h"]:
            # fixed_component_values está em config.json e acessível via self.config
            estrato_values = self.config.fixed_component_values.get(estrato, {})
            value_str = estrato_values.get(service, "R$ 0,00")
            return self._parse_currency_string(value_str)
        elif service in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
            # Para eMULTI, o valor fixo (custeio) vem de config.json['data'][service]['valor']
            service_info = self.config.get_service_info(service)
            value_str = service_info.get('valor', "R$ 0,00")
            return self._parse_currency_string(value_str)
        return 0.0
    
    def _get_service_value_from_config(self, service: str, edited_values: Dict[str, float]) -> float:
        """Obtém valor de um serviço do config.json."""
        if service in edited_values:
            return edited_values[service]
        
        service_data = self.config.get_service_info(service)
        if service_data and service_data.get('valor') != 'Sem cálculo':
            return self._parse_currency_string(service_data['valor'])
        
        return 0.0
    
    def _parse_currency_string(self, value_str: str) -> float:
        """Converte string de moeda para float."""
        try:
            return float(value_str.replace('R$ ', '').replace('.', '').replace(',', '.'))
        except (ValueError, AttributeError):
            return 0.0
    
    def _calculate_implantacao_rows(self, service_selection: ServiceSelection) -> Tuple[float, List[List]]:
        """Calcula as linhas de implantação para o componente fixo (eSF, eAP, eMulti)."""
        implantacao_rows = []
        total_implantacao_geral = 0
        
        implantacao_mapping = {
            "eMULTI Ampl.": "eMulti Ampliada",
            "eMULTI Compl.": "eMulti Complementar", 
            "eMULTI Estrat.": "eMulti Estratégica"
        }
        
        config_implantacao_values = self.config.implantacao_values
        
        # Considerar apenas serviços que podem ter implantação (eSF, eAP, eMulti)
        servicos_com_implantacao = ["eSF", "eAP 30h", "eAP 20h", "eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]

        for service in servicos_com_implantacao:
            # A quantidade de CUSTEIO do serviço deve ser > 0 para considerar implantação
            # E a quantidade de IMPLANTAÇÃO deve ser > 0
            if service_selection.services.get(service, 0) > 0: # Verifica se o serviço de custeio existe
                quantity_implantacao = service_selection.edited_implantacao_quantity.get(service, 0)
                
                if quantity_implantacao > 0:
                    if service in service_selection.edited_implantacao_values:
                        valor_implantacao = service_selection.edited_implantacao_values[service]
                    else:
                        valor_implantacao_str = "R$ 0,00"
                        if service in config_implantacao_values:
                            valor_implantacao_str = config_implantacao_values[service]
                        elif service in implantacao_mapping and implantacao_mapping[service] in config_implantacao_values:
                            valor_implantacao_str = config_implantacao_values[implantacao_mapping[service]]
                        valor_implantacao = self._parse_currency_string(valor_implantacao_str)
                    
                    total_implantacao_service = valor_implantacao * quantity_implantacao
                    total_implantacao_geral += total_implantacao_service
                    
                    implantacao_rows.append([
                        f"{service} (Implantação)", 
                        format_currency(valor_implantacao), 
                        quantity_implantacao, 
                        format_currency(total_implantacao_service)
                    ])
        
        return total_implantacao_geral, implantacao_rows

def calculate_incentive_totals(selected_services, service_values, base_data_config):
    """
    Calcula o valor total para os serviços de incentivo selecionados.
    Esta função é uma versão refatorada de calculate_total de calc_mais_gestor.py.

    Args:
        selected_services (dict): Dicionário com {nome_servico: quantidade}.
        service_values (dict): Dicionário com {nome_servico: valor_unitario_editado_pelo_usuario}.
        base_data_config (dict): Dicionário com a configuração base dos serviços (vindo de config.json['data']).

    Returns:
        list: Lista de listas, onde cada sublista representa uma linha da tabela de resultados,
              incluindo o total geral.
    """
    results = []
    total_geral = 0

    for service, quantity in selected_services.items():
        if quantity > 0 and service in base_data_config:
            # Usa o valor editado pelo usuário (de service_values) ou o valor padrão de base_data_config
            valor_str = service_values.get(service, base_data_config[service].get('valor'))
            
            if valor_str == 'Sem cálculo' or valor_str is None:
                valor_unitario = 0
            else:
                try:
                    # Remove "R$", espaços, troca separador de milhar e decimal
                    valor_unitario = float(str(valor_str).replace('R$', '').strip().replace('.', '').replace(',', '.'))
                except ValueError:
                    valor_unitario = 0 # Tratar erro se o valor não for conversível
            
            total_servico = valor_unitario * quantity
            total_geral += total_servico
            results.append([service, quantity, format_currency(valor_unitario), format_currency(total_servico)])

    if total_geral > 0:
        results.append(['Total Geral', '', '', format_currency(total_geral)])
    
    # Adiciona uma linha vazia se não houver resultados para garantir que a tabela seja exibida
    if not results:
        results.append(['Nenhum serviço selecionado','','',''])
        
    return results
