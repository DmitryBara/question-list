from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db import models, IntegrityError
from users.models import User


class Questionnaire(models.Model):
	"""
	Questionnaire list contain set of related questions.
	Only user who create questionnaire could manage it.

	- ordered_question_ids: Store ordered ids of questions. Example: ",2,34,7,16,".
	PROS: Reducing database load. For re-ordering or delete question we just operate with this field.
	CONS: Database engine do not manage relations into this TextField. We need to pay extra attention to that.
	"""
	title = models.CharField(max_length=250, unique=True)
	user_creator = models.ForeignKey(User, on_delete=models.PROTECT)
	ordered_question_ids = ArrayField(models.PositiveSmallIntegerField())

	def save(self, *args, **kwargs):
		try:
			super().save(*args, **kwargs)
		except IntegrityError as err:
			if err.__cause__.pgcode == '23505' and 'Key (title)' in str(err):
				raise ValueError('Questionnaire with same title already exist.')
			raise err


class Question(models.Model):
	"""
	Question text provided by author of questionnaire.
	Right now "answer_type" could be only AnswerType.SHORT_ANSWER according to technical assignment.
	We also do not implement answers logic yet (AnswerPrepared, AnswerCustom, Answer) only make db design.

	- is_active: False if Question is deleted (actually hided) from Questionnaire
	"""
	class AnswerType(models.TextChoices):
		SHORT_ANSWER = 'short_answer', 'Short answer'
		PARAGRAPH = 'paragraph', 'Paragraph'
		CHECKBOXES = 'checkboxes', 'Checkboxes'
		MULTIPLE_CHOICE = 'multiple_choice', 'Multiple choice'
		DROPDOWN = 'dropdown', 'Dropdown'

	questionnaire = models.ForeignKey(Questionnaire, on_delete=models.PROTECT)
	text = models.CharField(max_length=250)
	answer_type = models.CharField(max_length=15, choices=AnswerType.choices)
	is_active = models.BooleanField()

	class Meta:
		unique_together = (
			('questionnaire', 'text'),
		)

	def save(self, *args, **kwargs):
		try:
			super().save(*args, **kwargs)
		except IntegrityError as err:
			if err.__cause__.pgcode == '23505' and 'Key (questionnaire_id, text)' in str(err):
				raise ValueError('Question with same text already exist in current questionnaire.')
			raise err


class AnswerPrepared(models.Model):
	"""
	Prepared answer for Question with answer_type CHECKBOXES, MULTIPLE_CHOICE, DROPDOWN

	- is_active: False if AnswerPrepared is deleted (actually hided) from answer options to Question
	"""
	question = models.ForeignKey(Question, on_delete=models.PROTECT)
	text = models.CharField(max_length=250)
	is_active = models.BooleanField(default=True)


class AnswerCustom(models.Model):
	"""
	User answer for Question with answer_type SHORT_ANSWER, PARAGRAPH
	If different users make the same answer for question, we do not duplicate records in this table
	We will make records about it in Answer table.
	"""
	question = models.ForeignKey(Question, on_delete=models.PROTECT)
	text = models.TextField()


class Answer(models.Model):
	"""
	Store user answers.

	- content_type - could be AnswerPrepared or AnswerCustom
	"""
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')
