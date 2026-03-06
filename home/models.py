from django.db import models

# Create your models here.
class Barbeiros(models.Model):
    nome = models.CharField(max_length=255)
    sobre = models.TextField(max_length=1500)
    def __str__(self):
        return self.nome
class Usuarios(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=255) # Armazenará o hash da senha
    codigo_redf = models.IntegerField(default=0)
    e_barbeiro = models.BooleanField(default=False)
    nome_barbeiro = models.ForeignKey(Barbeiros, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.nome
    

class Location(models.Model):
    endereco = models.CharField(max_length=255)
    link_map = models.URLField(default="#")
    def __str__(self):
        return self.endereco
    



duracao_choices = [
    (15, '15 min'),
    (30, '30 min'),
    (60, '60 min'),
]
class Servicos(models.Model):
    titulo = models.CharField(max_length=100, default="")
    preco = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    duracao_minutos = models.PositiveIntegerField(default=30, choices=duracao_choices)
    def __str__(self):
        return self.titulo





    

class Agendamentos(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True)
    servico = models.CharField(max_length=10000, default="")
    barbeiro = models.ForeignKey(Barbeiros, on_delete=models.CASCADE)
    data = models.DateTimeField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    preco_total = models.CharField(max_length=100, null=True)


from django.db import models

class Expediente(models.Model):
    DIA_SEMANA_CHOICES = [
        (0, 'Segunda'),
        (1, 'Terça'),
        (2, 'Quarta'),
        (3, 'Quinta'),
        (4, 'Sexta'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    dia_semana = models.IntegerField(choices=DIA_SEMANA_CHOICES)

    inicio_manha = models.TimeField(null=True, blank=True)
    fim_manha = models.TimeField(null=True, blank=True)

    inicio_tarde = models.TimeField(null=True, blank=True)
    fim_tarde = models.TimeField(null=True, blank=True)

    ativo = models.BooleanField(default=True)

    def __str__(self):
        return dict(self.DIA_SEMANA_CHOICES)[self.dia_semana]