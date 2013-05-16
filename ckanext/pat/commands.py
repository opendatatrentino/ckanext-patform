from ckan import model
from ckan.lib.cli import CkanCommand
from ckan.logic import get_action, NotFound

import logging
from ckanext.pat.plugin import CATEGORY_VOCAB, HOLDERS_VOCAB, COVERAGE_VOCAB
log = logging.getLogger()

CATEGORIES = [
    u"Ambiente",
    u"Attivita istituzionale",
    u"Attivita politica",
    u"Conoscenza",
    u"Cultura",
    u"Demografia",
    u"Economia",
    u"Gestione del territorio",
    u"Meteo",
    u"Sicurezza",
    u"Sport",
    u"Welfare",
]

HOLDERS = [
    u"Provincia Autonoma di Trento",
    u"Consiglio della Provincia Autonoma di Trento",
    u"Consorzio dei Comuni",
    u"Fondazione Bruno Kessler",
    u"Fondazione Edmund Mach",
    u"Informatica Trentina",
    u"Trentino Network",
    u"Trentino Sviluppo",
    u"Trentino Trasporti Esercizio",
    u"Trentino Trasporti Infrastrutture",
    u"TrentoRise",
    u"Universita di Trento",
    u"Comune di Ala",
    u"Comune di Albiano",
    u"Comune di Aldeno",
    u"Comune di Amblar",
    u"Comune di Andalo",
    u"Comune di Arco",
    u"Comune di Avio",
    u"Comune di Baselga di Pin\xe8",
    u"Comune di Bedollo",
    u"Comune di Bersone",
    u"Comune di Besenello",
    u"Comune di Bieno",
    u"Comune di Bleggio Superiore",
    u"Comune di Bocenago",
    u"Comune di Bolbeno",
    u"Comune di Bondo",
    u"Comune di Bondone",
    u"Comune di Borgo Valsugana",
    u"Comune di Bosentino",
    u"Comune di Breguzzo",
    u"Comune di Brentonico",
    u"Comune di Bresimo",
    u"Comune di Brez",
    u"Comune di Brione",
    u"Comune di Caderzone Terme",
    u"Comune di Cagn\xf2",
    u"Comune di Calavino",
    u"Comune di Calceranica al Lago",
    u"Comune di Caldes",
    u"Comune di Caldonazzo",
    u"Comune di Calliano",
    u"Comune di Campitello di Fassa",
    u"Comune di Campodenno",
    u"Comune di Canal San Bovo",
    u"Comune di Canazei",
    u"Comune di Capriana",
    u"Comune di Carano",
    u"Comune di Carisolo",
    u"Comune di Carzano",
    u"Comune di Castel Condino",
    u"Comune di Castelfondo",
    u"Comune di Castello Tesino",
    u"Comune di Castello-Molina di Fiemme",
    u"Comune di Castelnuovo",
    u"Comune di Cavalese",
    u"Comune di Cavareno",
    u"Comune di Cavedago",
    u"Comune di Cavedine",
    u"Comune di Cavizzana",
    u"Comune di Cembra",
    u"Comune di Centa San Nicol\xf2",
    u"Comune di Cimego",
    u"Comune di Cimone",
    u"Comune di Cinte Tesino",
    u"Comune di Cis",
    u"Comune di Civezzano",
    u"Comune di Cles",
    u"Comune di Cloz",
    u"Comune di Comano Terme",
    u"Comune di Commezzadura",
    u"Comune di Condino",
    u"Comune di Coredo",
    u"Comune di Croviana",
    u"Comune di Cunevo",
    u"Comune di Daiano",
    u"Comune di Dambel",
    u"Comune di Daone",
    u"Comune di Dar\xe8",
    u"Comune di Denno",
    u"Comune di Dimaro",
    u"Comune di Don",
    u"Comune di Dorsino",
    u"Comune di Drena",
    u"Comune di Dro",
    u"Comune di Faedo",
    u"Comune di Fai della Paganella",
    u"Comune di Faver",
    u"Comune di Fiav\xe8",
    u"Comune di Fiera di Primiero",
    u"Comune di Fierozzo",
    u"Comune di Flavon",
    u"Comune di Folgaria",
    u"Comune di Fondo",
    u"Comune di Fornace",
    u"Comune di Frassilongo",
    u"Comune di Garniga Terme",
    u"Comune di Giovo",
    u"Comune di Giustino",
    u"Comune di Grauno",
    u"Comune di Grigno",
    u"Comune di Grumes",
    u"Comune di Imer",
    u"Comune di Isera",
    u"Comune di Ivano-Fracena",
    u"Comune di Lardaro",
    u"Comune di Lasino",
    u"Comune di Lavarone",
    u"Comune di Lavis",
    u"Comune di Ledro",
    u"Comune di Levico Terme",
    u"Comune di Lisignago",
    u"Comune di Livo",
    u"Comune di Lona-Lases",
    u"Comune di Luserna",
    u"Comune di Mal\xe8",
    u"Comune di Malosco",
    u"Comune di Massimeno",
    u"Comune di Mazzin",
    u"Comune di Mezzana",
    u"Comune di Mezzano",
    u"Comune di Mezzocorona",
    u"Comune di Mezzolombardo",
    u"Comune di Moena",
    u"Comune di Molveno",
    u"Comune di Monclassico",
    u"Comune di Montagne",
    u"Comune di Mori",
    u"Comune di Nago-Torbole",
    u"Comune di Nanno",
    u"Comune di Nave San Rocco",
    u"Comune di Nogaredo",
    u"Comune di Nomi",
    u"Comune di Novaledo",
    u"Comune di Ospedaletto",
    u"Comune di Ossana",
    u"Comune di Padergnone",
    u"Comune di Pal\xf9 del Fersina",
    u"Comune di Panchia",
    u"Comune di Peio",
    u"Comune di Pellizzano",
    u"Comune di Pelugo",
    u"Comune di Pergine Valsugana",
    u"Comune di Pieve di Bono",
    u"Comune di Pieve Tesino",
    u"Comune di Pinzolo",
    u"Comune di Pomarolo",
    u"Comune di Pozza di Fassa",
    u"Comune di Praso",
    u"Comune di Predazzo",
    u"Comune di Preore",
    u"Comune di Prezzo",
    u"Comune di Rabbi",
    u"Comune di Ragoli",
    u"Comune di Rev\xf2",
    u"Comune di Riva del Garda",
    u"Comune di Romallo",
    u"Comune di Romeno",
    u"Comune di Roncegno Terme",
    u"Comune di Ronchi Valsugana",
    u"Comune di Roncone",
    u"Comune di Ronzo-Chienis",
    u"Comune di Ronzone",
    u"Comune di Rover\xe8 della Luna",
    u"Comune di Rovereto",
    u"Comune di Ruffr\xe8-Mendola",
    u"Comune di Rumo",
    u"Comune di Sagron Mis",
    u"Comune di Samone",
    u"Comune di San Lorenzo in Banale",
    u"Comune di San Michele all'Adige",
    u"Comune di Sant'Orsola Terme",
    u"Comune di Sanzeno",
    u"Comune di Sarnonico",
    u"Comune di Scurelle",
    u"Comune di Segonzano",
    u"Comune di Sfruz",
    u"Comune di Siror",
    u"Comune di Smarano",
    u"Comune di Soraga",
    u"Comune di Sover",
    u"Comune di Spera",
    u"Comune di Spiazzo",
    u"Comune di Spormaggiore",
    u"Comune di Sporminore",
    u"Comune di Stenico",
    u"Comune di Storo",
    u"Comune di Strembo",
    u"Comune di Strigno",
    u"Comune di Taio",
    u"Comune di Tassullo",
    u"Comune di Telve",
    u"Comune di Telve di Sopra",
    u"Comune di Tenna",
    u"Comune di Tenno",
    u"Comune di Terlago",
    u"Comune di Terragnolo",
    u"Comune di Terres",
    u"Comune di Terzolas",
    u"Comune di Tesero",
    u"Comune di Tione di Trento",
    u"Comune di Ton",
    u"Comune di Tonadico",
    u"Comune di Torcegno",
    u"Comune di Trambileno",
    u"Comune di Transacqua",
    u"Comune di Trento",
    u"Comune di Tres",
    u"Comune di Tuenno",
    u"Comune di Valda",
    u"Comune di Valfloriana",
    u"Comune di Vallarsa",
    u"Comune di Varena",
    u"Comune di Vattaro",
    u"Comune di Vermiglio",
    u"Comune di Verv\xf2",
    u"Comune di Vezzano",
    u"Comune di Vignola-Falesina",
    u"Comune di Vigo di Fassa",
    u"Comune di Vigo Rendena",
    u"Comune di Vigolo Vattaro",
    u"Comune di Villa Agnedo",
    u"Comune di Villa Lagarina",
    u"Comune di Villa Rendena",
    u"Comune di Volano",
    u"Comune di Zambana",
    u"Comune di Ziano di Fiemme",
    u"Comune di Zuclo",
    u"Comunit\xe0 territoriale della Val di Fiemme",
    u"Comunit\xe0 di Primiero",
    u"Comunit\xe0 Valsugana e Tesino",
    u"Comunit\xe0 Alta Valsugana e Bersntol",
    u"Comunit\xe0 della Valle di Cembra",
    u"Comunit\xe0 della Val di Non",
    u"Comunit\xe0 della Valle di Sole",
    u"Comunit\xe0 delle Giudicarie",
    u"Comunit\xe0 Alto Garda e Ledro",
    u"Comunit\xe0 della Vallagarina",
    u"Comun General de Fascia",
    u"Magnifica Comunit\xe0 degli Altipiani cimbri",
    u"Comunit\xe0 Rotaliana-Koenigsberg",
    u"Comunit\xe0 della Paganella",
    u"Territorio della Val d'Adige",
    u"Comunit\xe0 della Valle dei Laghi",
]

COVERAGE = [u"Ala", u"Albiano", u"Aldeno", u"Altra area che interessa la Provincia di Trento", u"Altra area fuori della Provincia di Trento", u"Altro", u"Amblar", u"Andalo", 
            u"Arco", u"Avio", u"Baselga di Pin\xe8", u"Bedollo", u"Bersone", u"Besenello", u"Bieno", u"Bleggio Superiore", u"Bocenago", u"Bolbeno", u"Bondo", u"Bondone", 
            u"Borgo Valsugana", u"Bosentino", u"Breguzzo", u"Brentonico", u"Bresimo", u"Brez", u"Brione", u"Caderzone Terme", u"Cagn\xf2", u"Calavino", u"Calceranica al Lago", 
            u"Caldes", u"Caldonazzo", u"Calliano", u"Campitello di Fassa", u"Campodenno", u"Canal San Bovo", u"Canazei", u"Capriana", u"Carano", u"Carisolo", u"Carzano", u"Castel Condino", 
            u"Castelfondo", u"Castello Tesino", u"Castello-Molina di Fiemme", u"Castelnuovo", u"Cavalese", u"Cavareno", u"Cavedago", u"Cavedine", u"Cavizzana", u"Cembra", 
            u"Centa San Nicol\xf2", u"Cimego", u"Cimone", u"Cinte Tesino", u"Cis", u"Civezzano", u"Cles", u"Cloz", u"Comano Terme", u"Commezzadura", u"Comun General de Fascia", 
            u"Comunit\xe0 Alta Valsugana e Bersntol", u"Comunit\xe0 Alto Garda e Ledro", u"Comunit\xe0 Rotaliana-Koenigsberg", u"Comunit\xe0 Valsugana e Tesino", u"Comunit\xe0 della Paganella", 
            u"Comunit\xe0 della Val di Non", u"Comunit\xe0 della Vallagarina", u"Comunit\xe0 della Valle dei Laghi", u"Comunit\xe0 della Valle di Cembra", u"Comunit\xe0 della Valle di Sole", 
            u"Comunit\xe0 delle Giudicarie", u"Comunit\xe0 di Primiero", u"Comunit\xe0 territoriale della Val di Fiemme", u"Condino", u"Coredo", u"Croviana", u"Cunevo", u"Daiano", 
            u"Dambel", u"Daone", u"Dar\xe8", u"Denno", u"Dimaro", u"Don", u"Dorsino", u"Drena", u"Dro", u"Faedo", u"Fai della Paganella", u"Faver", u"Fiav\xe8", u"Fiera di Primiero", 
            u"Fierozzo", u"Flavon", u"Folgaria", u"Fondo", u"Fornace", u"Frassilongo", u"Garniga Terme", u"Giovo", u"Giustino", u"Grauno", u"Grigno", u"Grumes", u"Imer", u"Isera", 
            u"Ivano-Fracena", u"Lardaro", u"Lasino", u"Lavarone", u"Lavis", u"Ledro", u"Levico Terme", u"Lisignago", u"Livo", u"Lona-Lases", u"Luserna", u"Magnifica Comunit\xe0 degli Altipiani cimbri", 
            u"Malosco", u"Mal\xe8", u"Massimeno", u"Mazzin", u"Mezzana", u"Mezzano", u"Mezzocorona", u"Mezzolombardo", u"Moena", u"Molveno", u"Monclassico", u"Montagne", 
            u"Mori", u"Nago-Torbole", u"Nanno", u"Nave San Rocco", u"Nogaredo", u"Nomi", u"Novaledo", u"Ospedaletto", u"Ossana", u"Padergnone", u"Pal\xf9 del Fersina", u"Panchia", 
            u"Peio", u"Pellizzano", u"Pelugo", u"Pergine Valsugana", u"Pieve Tesino", u"Pieve di Bono", u"Pinzolo", u"Pomarolo", u"Pozza di Fassa", u"Praso", u"Predazzo", u"Preore", 
            u"Prezzo", u"Provincia di Trento", u"Rabbi", u"Ragoli", u"Rev\xf2", u"Riva del Garda", u"Romallo", u"Romeno", u"Roncegno Terme", u"Ronchi Valsugana", u"Roncone", 
            u"Ronzo-Chienis", u"Ronzone", u"Rovereto", u"Rover\xe8 della Luna", u"Ruffr\xe8-Mendola", u"Rumo", u"Sagron Mis", u"Samone", u"San Lorenzo in Banale", 
            u"San Michele all Adige", u"Sant Orsola Terme", u"Sanzeno", u"Sarnonico", u"Scurelle", u"Segonzano", u"Sfruz", u"Siror", u"Smarano", u"Soraga", u"Sover", 
            u"Spera", u"Spiazzo", u"Spormaggiore", u"Sporminore", u"Stenico", u"Storo", u"Strembo", u"Strigno", u"Taio", u"Tassullo", u"Telve", u"Telve di Sopra", u"Tenna", 
            u"Tenno", u"Terlago", u"Terragnolo", u"Terres", u"Territorio della Val d Adige", u"Terzolas", u"Tesero", u"Tione di Trento", u"Ton", u"Tonadico", u"Torcegno",
            u"Trambileno", u"Transacqua", u"Trento", u"Tres", u"Tuenno", u"Valda", u"Valfloriana", u"Vallarsa", u"Varena", u"Vattaro", u"Vermiglio", u"Verv\xf2", 
            u"Vezzano", u"Vignola-Falesina", u"Vigo Rendena", u"Vigo di Fassa", u"Vigolo Vattaro", u"Villa Agnedo", u"Villa Lagarina", u"Villa Rendena", 
            u"Volano", u"Zambana", u"Ziano di Fiemme", u"Zuclo"]

VOCABS = {CATEGORY_VOCAB: CATEGORIES, 
          HOLDERS_VOCAB: HOLDERS, 
          COVERAGE_VOCAB: COVERAGE}


class PatCommand(CkanCommand):
    '''
    CKAN Example Extension

    Usage::

        paster pat create-vocabs -c <path to config file>

        paster pat add-term <vocab_name> <new_term> -c <path to config file>
        
        paster pat remove-term <vocab_name> <term_to_remove> -c <path to config file>
        
        paster pat clean -c <path to config file>
            - Remove all data created by ckanext-pat

    The commands should be run from the ckanext-pat directory.
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def command(self):
        '''
        Parse command line arguments and call appropriate method.
        '''
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print PatCommand.__doc__
            return

        cmd = self.args[0]
        self._load_config()

        if cmd == 'create-vocabs':
            self.create_pat_vocabs()
        elif cmd == 'add-term':
            vocab_name = self.args[1]
            new_term = self.args[2]
            self.add_term_to_pat_vocabs(vocab_name, new_term)
        elif cmd == 'remove-term':
            vocab_name = self.args[1]
            term_to_remove = self.args[2]
            self.remove_term_from_pat_vocabs(vocab_name, term_to_remove)
        elif cmd == 'clean':
            self.clean()
        else:
            log.error('Command "%s" not recognized' % (cmd,))

    def create_pat_vocabs(self):
        '''
        Adds pat vocabularies to the database if they don't already exist.
        '''
        user = get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
        context = {'model': model, 'session': model.Session, 'user': user['name']}
        
        for label in VOCABS.keys():
            try:
                data = {'id': label}
                get_action('vocabulary_show')(context, data)
                log.info("Example genre vocabulary already exists, skipping.")
            except NotFound:
                terms = VOCABS[label]
                data = {'name': label}
                vocab = get_action('vocabulary_create')(context, data)
                print terms;
                for term in terms:
                    data = {'name': term, 'vocabulary_id': vocab['id']}
                    get_action('tag_create')(context, data)

    def add_term_to_pat_vocabs(self, vocab_name, new_term):
        '''
        Adds a new term to a pat-vocabulary to the database.
        '''
        user = get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
        context = {'model': model, 'session': model.Session, 'user': user['name']}
        
        vocab_data = {'id': vocab_name}
        try:
            vocab = get_action('vocabulary_show')(context, vocab_data)
        except NotFound:
            available_vocabs = [CATEGORY_VOCAB, HOLDERS_VOCAB, COVERAGE_VOCAB]
            log.error('Vocabulary "%s" not exists!\r\nAvailable vocabularies are: %s'%(vocab_name,available_vocabs,))
            return
        
        term_data = {'name': new_term, 'vocabulary_id': vocab['id']}
        get_action('tag_create')(context, term_data)
        log.info('Term "%s" added to vocabulary "%s"'%(new_term, vocab_name,))
        print 'Term "%s" added to vocabulary "%s"'%(new_term, vocab_name,)

    def remove_term_from_pat_vocabs(self, vocab_name, term_to_remove):
        '''
        Remove a term from a pat-vocabulary from the database.
        '''
        user = get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
        context = {'model': model, 'session': model.Session, 'user': user['name']}
        
        vocab_data = {'id': vocab_name}
        try:
            vocab = get_action('vocabulary_show')(context, vocab_data)
        except NotFound:
            available_vocabs = [CATEGORY_VOCAB, HOLDERS_VOCAB, COVERAGE_VOCAB]
            log.error('Vocabulary "%s" not exists!\r\nAvailable vocabularies are: %s'%(vocab_name,available_vocabs,))
            return
        
        term_data = {'id': term_to_remove, 'vocabulary_id': vocab['id']}

        get_action('tag_delete')(context, term_data)
        log.info('Term "%s" removed from vocabulary "%s"'%(term_to_remove, vocab_name,))
        print 'Term "%s" removed from vocabulary "%s"'%(term_to_remove, vocab_name,)

    def clean(self):
        user = get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
        context = {'model': model, 'session': model.Session, 'user': user['name']}
        for vocab in VOCABS.keys():
            data = {'vocab_id': vocab, 'id': vocab}
            get_action('vocabulary_delete')(context, data)
