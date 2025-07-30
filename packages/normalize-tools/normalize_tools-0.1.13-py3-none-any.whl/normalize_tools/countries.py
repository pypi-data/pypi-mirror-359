import csv
from unidecode import unidecode
from babel import Locale, UnknownLocaleError
from typing import Dict, List, Optional, Set, Tuple
from normalize_tools.traductions import traducciones, unique_languages, ISO_NORMALIZADO
from functools import reduce
import re
import tldextract
import pycountry
import phonenumbers
from phonenumbers import NumberParseException, parse, is_valid_number, region_code_for_number
import geocoder

def strip_parenthesis(nombre: str) -> str:
    return re.sub(r"\s+\(.*?\)$", "", nombre)

# Descartar particulas de los principales idiomas es, en, fr, de
stop_particles = {
    # Incluyo republica por que da falsos positivos a la primera encontrada Congo
    "es": {
        "el", "la", "los", "las", "un", "una", "unos", "unas",
        "de", "del", "al", "a", "en", "por", "para", "con", "sin", "sobre",
        "entre", "tras", "hacia", "hasta",
        "y", "o", "u", "ni", "que", "como", "pero", "republica"
    },
    "en": {
        "the", "a", "an",
        "of", "in", "on", "at", "by", "with", "without", "about", "against",
        "from", "to", "into", "over", "under",
        "and", "or", "nor", "but", "so", "yet", "republic"
    },
    "fr": {
        "le", "la", "les", "un", "une", "des", "du", "de", "au", "aux",
        "en", "dans", "avec", "sans", "par", "pour", "sur", "sous", "chez",
        "et", "ou", "ni", "mais", "que", "dont", "comme", "republique"
    },
    "de": {
        "der", "die", "das", "ein", "eine", "einer", "eines", "einem", "einen",
        "den", "dem", "des",
        "von", "zu", "mit", "nach", "aus", "über", "unter", "für", "ohne",
        "um", "an", "auf", "in", "bei", "zwischen",
        "und", "oder", "aber", "sondern", "doch", "denn", "republik"
    }
}

def tokenize(text: str, stop_particles: Dict[str, set] = stop_particles) -> Set[str]:
    tokens = text.split()
    all_stop_particles = reduce(set.union, stop_particles.values())
    return {t for t in tokens if t not in all_stop_particles}

# Formatear nombres
def normalize(n: Optional[str]) -> str:
    # Normaliza cadenas eliminando tildes, convirtiendo a minúsculas y eliminando espacios
    if n is None or n == "":
        return ""
    return unidecode(str(n).strip().lower())

def get_translations_for_country(iso_code, unique_languages):
    # Devuelve una lista de traducciones normalizadas del nombre de un país para cada idioma dado
    translations = []
    for lang in unique_languages:
        try:
            name = Locale(lang).territories.get(iso_code)
            if name:
                translations.append(normalize(name))
        except (UnknownLocaleError, KeyError):
            continue
    return translations

def read_csv_file(filename: str) -> List[Dict[str, str]]:
    """
    Lee un archivo CSV y devuelve una lista de diccionarios.
    """
    data = []
    try:
        with open(filename, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Warning: File {filename} not found")
    except Exception as e:
        print(f"Error reading {filename}: {e}")
    return data

def get_unique_values_from_column(data: List[Dict[str, str]], column_name: str) -> List[str]:
    """
    Obtiene valores únicos de una columna, excluyendo valores vacíos o None.
    """
    values = set()
    for row in data:
        value = row.get(column_name, "").strip()
        if value and value.lower() != 'none':
            values.add(value)
    return list(values)

def create_datastructures(countries_file="data/origin_country.csv", languages_file="data/idiomas_x_pais.csv"):
    # Crea las listas de países e idiomas y añade traducciones a los países
    
    countries_data = read_csv_file(countries_file)
    languages_data = read_csv_file(languages_file)
    
    # Obtener idiomas únicos
    unique_languages = get_unique_values_from_column(languages_data, 'language_code')
    
    # Añadir traducciones a cada país
    for country in countries_data:
        country_code = country.get('code', '')
        if country_code:
            country['translations'] = get_translations_for_country(country_code, unique_languages)
        else:
            country['translations'] = []
    
    return countries_data, unique_languages

def build_lookup_index(countries_data: List[Dict[str, str]]) -> Dict[str, str]:
    # Construye un diccionario de búsqueda rápida (lookup) con variantes normalizadas del nombre del país
    
    lookup: Dict[str, str] = {}
    for country in countries_data:
        name_es: str = country.get('name_es', '')
        translations: List[str] = country.get('translations', [])

        for variant in translations:
            if variant and variant not in lookup:
                lookup[variant] = name_es

    return lookup

# Diccionario precargado con las traducciones disponibles (importado)
lookup_index = traducciones

def search_country_name(user_input: str, lookup_index: Dict[str, str] = lookup_index) -> str:
    user_input = normalize(user_input)
    if not user_input:
        return ""
    
    input_tokens = tokenize(user_input)

    for key, value in lookup_index.items():
        key_tokens = set(key.split())
        if input_tokens == key_tokens:
            return strip_parenthesis(value)

    for key, value in lookup_index.items():
        key_tokens = set(key.split())
        if input_tokens.issubset(key_tokens):
            return strip_parenthesis(value)

    return ""

def get_region(pais: str) -> str:
    """
    Clasifica un país en una de las tres regiones: 'España', 'LATAM', 'Otros'.
    
    Parámetros:
    pais (str): Nombre del país ya normalizado.
    
    Retorno:
    str: 'España', 'LATAM', 'Otros' o '' si el país no está en la lista.
    """

    errores = ['Reino Unido', 'Territorio Británico del Océano Índico',
       'Estados Unidos', 'República Dominicana', 'Gambia', 'Filipinas',
       'Países Bajos', 'Irán', 'Emiratos Árabes Unidos', 'Níger', 'Sudán']

    paises_es = {"España"}
    paises_latam = {
        'Venezuela, República Bolivariana de', 'El Salvador', 'Panamá', 'Jamaica', 'Costa Rica', 'Paraguay', 'Granada', 'Belice', 'Barbados', 'Argentina', 'Perú', 'San Cristóbal y Nieves', 'Honduras', 'Colombia', 'República Dominicana', 'Surinam', 'Ecuador', 'Santa Lucía', 'Brasil', 'San Vicente y las Granadinas', 'México', 'Guyana', 'Bahamas', 'Nicaragua', 'Trinidad y Tobago', 'Chile', 'Antigua y Barbuda', 'Haití', 'Cuba', 'Dominica', 'Uruguay', 'Bolivia, Estado Plurinacional de', 'Guatemala'
    }

    paises_resto = {'Macao', 'Países Bajos', 'Sri Lanka', 'Hong Kong', 'Islas Caimán', 'Taiwán', 'Svalbard y Jan Mayen', 'Botsuana', 'Turquía', 'Guernsey', 'Uganda', 'Nueva Zelanda', 'Lao, (la) República Democrática Popular', 'Mauritania', 'Bielorrusia', 'Uzbekistán', 'Ghana', 'Anguila', 'Malaui', 'Eslovenia', 'Pitcairn', 'Andorra', 'Italia', 'Corea', 'Kuwait', 'Malí', 'Antártida', 'Territorios Australes Franceses', 'Curaçao', 'Kenia', 'Kiribati', 'Liechtenstein', 'Ruanda', 'Bosnia y Herzegovina', 'Aruba', 'Emiratos Árabes Unidos', 'Mauricio', 'Islas Marshall', 'Bután', 'Madagascar', 'Palestina, Estado de', 'Gambia', 'Samoa Americana', 'Islas Marianas del Norte', 'Albania', 'Indonesia', 'Guinea', 'Guinea-Bisáu', 'Senegal', 'Grecia', 'Zimbabue', 'Libia', 'Islas Turcas y Caicos', 'Catar', 'Eritrea', 'Rumania', 'Japón', 'Arabia Saudita', 'Noruega', 'Filipinas', 'Zambia', 'Puerto Rico', 'Cabo Verde', 'Moldavia', 'Santa Sede[Estado de la Ciudad del Vaticano]', 'Bélgica', 'Guam', 'Sudán', 'Camerún', 'Liberia', 'Mayotte', 'Mozambique', 'Finlandia', 'Nepal', 'Corea', 'San Marino', 'Estados Unidos', 'Bulgaria', 'Bangladés', 'Comoras', 'Suazilandia', 'China', 'Estonia', 'Guadalupe', 'Samoa', 'Bermudas', 'Chipre', 'Groenlandia', 'Croacia', 'Jordania', 'Santa Elena, Ascensión y Tristán de Acuña', 'Ucrania', 'Micronesia', 'Montenegro', 'Somalia', 'Santo Tomé y Príncipe', 'Malasia', 'Tayikistán', 'Yemen', 'Austria', 'Myanmar', 'Marruecos', 'Camboya', 'Irak', 'Sahara Occidental', 'Congo', 'Tanzania, República Unida de', 'Tonga', 'Sudáfrica', 'Yibuti', 'Francia', 'Sudán del Sur', 'Vanuatu', 'Tokelau', 'Irlanda', 'Kirguistán', 'San Pedro y Miquelón', 'Territorio Británico del Océano Índico', 'Afganistán', 'Kazajistán', 'Papúa Nueva Guinea', 'Timor-Leste', 'Níger', 'Jersey', 'Pakistán', 'Portugal', 'Azerbaiyán', 'Gabón', 'Turkmenistán', 'Montserrat', 'Polonia', 'Guayana Francesa', 'Argelia', 'Fiyi', 'Letonia', 'Isla de Navidad', 'Canadá', 'Benín', 'Túnez', 'Alemania', 'Wallis y Futuna', 'Reunión', 'Omán', 'Siria, (la) República Árabe', 'Suiza', 'Luxemburgo', 'Armenia', 'Mongolia', 'San Bartolomé', 'Mónaco', 'Congo', 'Nueva Caledonia', 'Islas de Ultramar Menores de Estados Unidos', 'Lituania', 'Isla de Man', 'Reino Unido', 'Sierra Leona', 'Namibia', 'Dinamarca', 'Serbia', 'Sint Maarten', 'Palaos', 'Singapur', 'Niue', 'Isla Heard e Islas McDonald', 'Brunéi Darussalam', 'Israel', 'Cote d Ivoire', 'Baréin', 'Bonaire, San Eustaquio y Saba', 'Malta', 'Nauru', 'Islas Cook', 'Burkina Faso', 'Isla Norfolk', 'Islas Åland', 'Maldivas', 'Egipto', 'Islas Vírgenes', 'Islas Salomón', 'Polinesia Francesa', 'Angola', 'Chad', 'Isla Bouvet', 'Islas Malvinas [Falkland]', 'Tailandia', 'Suecia', 'India', 'Nigeria', 'Togo', 'Macedonia', 'República Centroafricana', 'Lesoto', 'Georgia del sur y las islas sandwich del sur', 'Tuvalu', 'Rusia, (la) Federación de', 'Australia', 'Martinica', 'Etiopía', 'Georgia', 'Islas Feroe', 'Eslovaquia', 'Viet Nam', 'Irán', 'Seychelles', 'Hungría', 'San Martín', 'Guinea Ecuatorial', 'Islandia', 'Islas Vírgenes', 'República Checa', 'Islas Cocos', 'Gibraltar', 'Líbano', 'Burundi'}
    if pais in paises_es:
        return "España"
    elif pais in paises_latam:
        return "LATAM"
    elif pais in paises_resto:  # Este conjunto debe contener todos los nombres del CSV
        return "Otros"
    else:
        return ""

def validar_local_part(local_part: str) -> bool:
    """
    Valida la parte local (antes del @) de una dirección de correo electrónico.
    No permite que empiece o termine en punto, ni caracteres fuera del conjunto permitido.
    """
    patron = re.compile(r"^(?!\.)[a-zA-Z0-9!#$%&'*+/=?^_`{|}~.-]{1,64}(?<!\.)$")
    return bool(patron.match(local_part))

def validar_dominio(dominio: str) -> bool:
    """
    Valida la estructura sintáctica de un dominio (parte derecha del email).
    Ej: dominio.com, sub.dominio.co.uk
    """
    if len(dominio) > 253:
        return False

    patron = re.compile(
        r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)'         # Primer label
        r'(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))+$'     # Uno o más labels después del punto
    )

    return bool(patron.fullmatch(dominio))

def infer_country_from_email(email: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Infiere el país de origen a partir del dominio de un correo electrónico (usando el ccTLD).
    
    Args:
        email: dirección de correo electrónico.

    Returns:
        country_code: código ISO alpha-2 si se infiere (por ejemplo, "ES"), o None.
        country_name_es: nombre largo del país en español (por ejemplo, "España"), o None.
    """
    try:
        # Validar el email
        if not isinstance(email, str) or "@" not in email:
            return None, None
        
        # Extraer dominio
        parts = email.split("@", 1)
        domain = parts[1].lower().strip()
        address = parts[0].lower().strip()

        if not validar_local_part(address) or not validar_dominio(domain):
            return None, None
        
        # Extraer sufijo usando tldextract
        ext = tldextract.extract(domain)
        suffix = ext.suffix
        
        if not suffix:
            return None, None
        
        # Dividir sufijo en partes e invertir el orden
        suffix_parts = suffix.split('.')
        part = suffix_parts[-1].upper()
        if part == "UK":
            part = "GB"
        
        # Recorrer partes buscando un código de país válido

        if len(part) == 2:
            try:
                # Intentar obtener el país desde pycountry
                country = pycountry.countries.get(alpha_2=part.upper())

                if country:
                    country_code = country.alpha_2
                    
                    # Obtener el nombre del país en español usando babel
                    try:
                        country_name_es = Locale('es').territories[country_code]
                    except (KeyError, AttributeError):
                        country_name_es = None
                        
                    return country_code, country_name_es

            except (AttributeError, KeyError):
                return None, None
        
        # No se encontró un código de país válido
        return None, None
        
    except (KeyError, AttributeError):
        # En caso de cualquier error no previsto, devolver None, None
        return None, None

ISO_NORMALIZADO = {
    "GG": "GB",  # Guernesey → Reino Unido
    "JE": "GB",  # Jersey → Reino Unido
    "IM": "GB",  # Isla de Man → Reino Unido
    "GF": "FR",  # Guayana Francesa → Francia
    "MQ": "FR",  # Martinica → Francia
    "GP": "FR",  # Guadalupe → Francia
    "NC": "FR",  # Nueva Caledonia → Francia
    "PF": "FR",  # Polinesia Francesa → Francia
    "RE": "FR",  # Reunión → Francia
    "YT": "FR",  # Mayotte → Francia
    "HK": "CN",  # Hong Kong → China
    "MO": "CN",  # Macao → China
    "TW": "CN",  # Taiwán → China
    "PS": "IL",  # Palestina → Israel
    "XK": "RS",  # Kosovo → Serbia
    "PR": "US",  # Puerto Rico → Estados Unidos
    "VI": "US",  # Islas Vírgenes EE. UU. → Estados Unidos
    "GU": "US",  # Guam → Estados Unidos
    "AS": "US",  # Samoa Americana → Estados Unidos
    "MP": "US",  # Marianas del Norte → Estados Unidos
    "CW": "NL",  # Curazao → Países Bajos
    "BQ": "NL",  # Bonaire → Países Bajos
    "SX": "NL",  # Sint Maarten → Países Bajos
    "AW": "NL",  # Aruba → Países Bajos
}

# Regiones prioritarias (puedes añadir más si lo deseas)
REGIONES_POR_DEFECTO = [
    # España
    "ES",

    # Centroamérica
    "MX", "GT", "SV", "HN", "NI", "CR", "PA",

    # Caribe hispano y afines
    "CU", "DO", "PR",  # Puerto Rico (territorio US)

    # Sudamérica
    "CO", "VE", "EC", "PE", "BO", "CL", "AR", "UY", "PY",

    # Brasil
    "BR",

    # Europa occidental
    "PT", "FR", "IT", "DE", "BE", "NL",

    # Europa central y oriental (por población migrante)
    "PL", "RO", "RU", "UA",

    # África relevante
    "MA", "DZ", "TN",  # Magreb
    "NG", "ZA",  # Nigeria, Sudáfrica

    # Asia relevante
    "CN", "JP", "IN", "PH", "PK", "KR", "VN",

    # Oriente Medio
    "TR", "IR", "SA", "IL",

    # Norteamérica
    "CA", "US",

    # Otros frecuentes en migración o presencia internacional
    "GB", "IE", "AU", "NZ",  # Anglohablantes
    "CH", "SE", "NO", "DK", "FI"  # Nórdicos
]

REGIONES_POR_DEFECTO_ = [
    "ES",  # España
    "MX", "GT", "SV", "HN", "NI", "CR", "PA",  # Centroamérica
    "CO", "VE", "EC", "PE", "BO", "CL", "AR", "UY", "PY",  # Sudamérica
    "BR",  # Brasil
    "PT", "FR", "IT", "DE", "BE", "NL",  # Europa occidental
    "CA", "US" # Norteamerica
]

def code_to_pair(country_code):
    country_code = ISO_NORMALIZADO.get(country_code, country_code)
    # Obtener el nombre del país en español
    try:
        locale_es = Locale('es')
        country_name_es = locale_es.territories.get(country_code, "")
        return country_code, country_name_es
    except:
        return "", ""


def detectar_pais(telefono: str, regiones=REGIONES_POR_DEFECTO) -> Tuple[Optional[str], Optional[str]]:
    telefono = str(telefono).strip()
    
    # 1. Intento como número internacional
    try:
        parsed = parse(telefono, None)
        if is_valid_number(parsed):
            return code_to_pair(region_code_for_number(parsed))
        

    except NumberParseException:
        pass

    # 2. Intento por regiones sugeridas
    for region in regiones:
        try:
            parsed = parse(telefono, region)
            if is_valid_number(parsed):
                return code_to_pair(region_code_for_number(parsed))
        
        except NumberParseException:
            continue

    return "", ""

def get_country_from_phone(original):
    """
    Obtiene el nombre del país en español de un número de teléfono.
    
    Args:
        original (str): Número de teléfono
        
    Returns:
        str: Nombre del país en español o cadena vacía si hay error
    """
    try:
        # Normalizar el número
        if not original.startswith('+'):
            if original.startswith('00'):
                numero = '+' + original[2:]
            else:
                numero = '+34' + original
        else:
            numero = original
        
        # Parsear el número
        parsed_number = phonenumbers.parse(numero)
        
        # Verificar si es un número válido
        is_valid = phonenumbers.is_valid_number(parsed_number)
        
        if not is_valid:
            # Intentar con +34 removido
            if numero.startswith("+34"):
                numero = f"+{numero[3:]}"
                parsed_number = phonenumbers.parse(numero)
                is_valid = phonenumbers.is_valid_number(parsed_number)
        
        if not is_valid:
            return ""
        
        # Obtener el código de país y normalizarlo
        country_code = phonenumbers.region_code_for_number(parsed_number)
        country_code = ISO_NORMALIZADO.get(country_code, country_code)
        
        # Obtener el nombre del país en español
        try:
            locale_es = Locale('es')
            country_name_es = locale_es.territories.get(country_code, "")
            return country_name_es
        except:
            return ""
            
    except (NumberParseException, Exception):
        return ""