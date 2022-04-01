import graphene
from django.db.models import Prefetch
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required
from questionnaire.models import Questionnaire, Question

# Enum converted from TextChoices specially for graphQL
AnswerType = graphene.Enum.from_enum(Question.AnswerType)

# Common argument for prefetch questions from database which are not deleted.
# This trick will reduce count of database operations
prefetch_questions = Prefetch('question_set', queryset=Question.objects.filter(is_active=True))


class QuestionnaireType(DjangoObjectType):
	class Meta:
		model = Questionnaire
		fields = '__all__'

	id = graphene.Int(source='pk')


class QuestionType(DjangoObjectType):
	class Meta:
		model = Question
		fields = '__all__'

	id = graphene.Int(source='pk')
	# answer_type = AnswerType()


class Query(graphene.ObjectType):
	questionnaire = graphene.List(QuestionnaireType)

	@staticmethod
	def resolve_questionnaire(root, info):
		return Questionnaire.objects.all().prefetch_related(prefetch_questions)


class CreateQuestionnaire(graphene.Mutation):
	class Arguments:
		title = graphene.String(required=True)

	questionnaire = graphene.Field(QuestionnaireType)

	@staticmethod
	@login_required
	def mutate(root, info, title):
		questionnaire = Questionnaire.objects.create(
			title=title,
			user_creator=info.context.user,
			ordered_question_ids=[],
		)

		return CreateQuestionnaire(questionnaire)


class CreateQuestion(graphene.Mutation):
	class Arguments:
		questionnaire_id = graphene.Int(required=True)
		text = graphene.String(required=True)
		answer_type = AnswerType(required=True)

	questionnaire = graphene.Field(QuestionnaireType)

	@staticmethod
	@login_required
	def mutate(root, info, questionnaire_id, text, answer_type):
		question = Question.objects.create(
			questionnaire_id=questionnaire_id,
			text=text,
			answer_type=answer_type,
			is_active=True,
		)

		questionnaire_queryset = Questionnaire.objects.filter(id=questionnaire_id).prefetch_related(prefetch_questions)
		questionnaire = questionnaire_queryset.first()
		if not questionnaire:
			raise ValueError(f"Questionnaire with provided id (questionnaire_id={questionnaire_id}) not found")
		if questionnaire.user_creator_id != info.context.user.id:
			raise PermissionError(f"Current user (user_id={info.context.user.id}) could not manage this questionnaire")
		questionnaire.ordered_question_ids.append(question.id)
		questionnaire.save()

		return CreateQuestion(questionnaire)


class DeleteQuestion(graphene.Mutation):
	class Arguments:
		questionnaire_id = graphene.Int(required=True)
		question_id = graphene.Int(required=True)

	questionnaire = graphene.Field(QuestionnaireType)

	@staticmethod
	@login_required
	def mutate(root, info, questionnaire_id, question_id):
		question = Question.objects.get(id=question_id, questionnaire_id=questionnaire_id)
		if not question.is_active:
			raise ValueError("Question is already deleted")
		question.is_active = False
		question.save()

		questionnaire_queryset = Questionnaire.objects.filter(id=questionnaire_id).prefetch_related(prefetch_questions)
		questionnaire = questionnaire_queryset.first()
		if questionnaire.user_creator_id != info.context.user.id:
			raise PermissionError(f"Current user (user_id={info.context.user.id}) could not manage this questionnaire")
		questionnaire.ordered_question_ids.remove(question.id)
		questionnaire.save()

		return DeleteQuestion(questionnaire)


class ReorderQuestions(graphene.Mutation):
	class Arguments:
		questionnaire_id = graphene.Int(required=True)
		ordered_question_ids = graphene.List(graphene.Int, required=True)

	questionnaire = graphene.Field(QuestionnaireType)

	@staticmethod
	@login_required
	def mutate(root, info, questionnaire_id, ordered_question_ids):
		questionnaire_queryset = Questionnaire.objects.filter(id=questionnaire_id).prefetch_related(prefetch_questions)
		questionnaire = questionnaire_queryset.first()
		if not questionnaire:
			raise ValueError(f"Questionnaire with provided id (questionnaire_id={questionnaire_id}) not found")
		if questionnaire.user_creator_id != info.context.user.id:
			raise PermissionError(f"Current user (user_id={info.context.user.id}) could not manage this questionnaire")

		is_content_matching = set(ordered_question_ids) == set(questionnaire.ordered_question_ids)
		is_count_matching = len(ordered_question_ids) == len(questionnaire.ordered_question_ids)
		is_matching = is_content_matching and is_count_matching
		if not is_matching:
			raise ValueError(f"Provided ordered_question_ids={ordered_question_ids} not matching "
							 f"with already existed ordered_question_ids={questionnaire.ordered_question_ids}")

		questionnaire.ordered_question_ids = ordered_question_ids
		questionnaire.save()

		return ReorderQuestions(questionnaire)


class Mutation(graphene.ObjectType):
	create_questionnaire = CreateQuestionnaire.Field()
	create_question = CreateQuestion.Field()
	delete_question = DeleteQuestion.Field()
	reorder_questions = ReorderQuestions.Field()
