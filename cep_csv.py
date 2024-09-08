import requests
from geopy.geocoders import Nominatim
import csv

# Lista de CEPs
ceps = ['37503130', '01001000', '01310100']

# Criar o geolocator
geolocator = Nominatim(user_agent="test_app")

# Função para buscar o endereço pelo CEP usando ViaCEP
def get_address_from_cep(cep):
    try:
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
        response.raise_for_status()  # Lançar exceção para códigos de status 4xx/5xx
        return response.json()  # Retorna o resultado em formato JSON
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter o endereço para o CEP {cep}: {e}")
        return None

# Função para geocodificar o endereço usando Nominatim
def geocode_address(address):
    full_address = f"{address['logradouro']}, {address['localidade']} - {address['bairro']}"
    try:
        location = geolocator.geocode(full_address)
        return location
    except Exception as e:
        print(f"Erro ao geocodificar o endereço {full_address}: {e}")
        return None

# Função principal para processar todos os CEPs e salvar os dados no CSV
def process_ceps():
    with open('localizacao.csv', mode='w', newline='') as file, open('ceps_falha.csv', mode='w', newline='') as error_file:
        writer = csv.writer(file)
        error_writer = csv.writer(error_file)
        
        # Cabeçalhos dos arquivos CSV
        writer.writerow(['CEP', 'Latitude', 'Longitude', 'Endereço'])
        error_writer.writerow(['CEP', 'Motivo da Falha'])

        for cep in ceps:
            address = get_address_from_cep(cep)

            # Verifica se o endereço contém os dados necessários
            if address and 'logradouro' in address and 'localidade' in address and 'bairro' in address:
                location = geocode_address(address)

                if location:
                    # Grava os dados de sucesso no CSV
                    writer.writerow([cep, location.latitude, location.longitude, f"{address['logradouro']}, {address['localidade']} - {address['bairro']}"])
                    print(f"Dados do CEP {cep} salvos com sucesso.")
                else:
                    # Registra no arquivo de falhas caso não consiga geocodificar
                    error_writer.writerow([cep, "Geocodificação falhou"])
                    print(f"Localização não encontrada para o CEP {cep}.")
            else:
                # Registra no arquivo de falhas caso o endereço esteja incompleto
                error_writer.writerow([cep, "Endereço incompleto"])
                print(f"Endereço incompleto para o CEP {cep}.")

    print("Processo concluído.")

# Executar o processo
process_ceps()
