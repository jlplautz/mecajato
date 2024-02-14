❯ python3 manage.py shell
Python 3.12.0 (main, Nov 21 2023, 10:59:00) [GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from mecajato.servicos.models import Servico
>>> serv = Servico.objects.get(id=1)
>>> serv.preco_total()
130.0
>>> 
