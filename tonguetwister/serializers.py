from rest_framework import serializers
from .models import OldPolish, Articulator, Funfact, Twister, Exercise, Trivia

class OldPolishSerializer(serializers.ModelSerializer):
    class Meta:
        model = OldPolish
        fields = ['id', 'old_text', 'new_text']

class ArticulatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articulator
        fields = ['id', 'text']

class FunfactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funfact
        fields = ['id', 'text']

class TwisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Twister
        fields = ['id', 'text']

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'text']

class TriviaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trivia
        fields = ['id', 'text']
