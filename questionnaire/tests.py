from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenTestCase


requested_data = """
	questionnaire {
		id,
		title,
		userCreator {
			email
		},
		orderedQuestionIds,
		questionSet {
			id
			text
			answerType
		}
	}
"""


class QuestionnaireGraphQLTest(JSONWebTokenTestCase):
	fixtures = [
		'fixtures/users/user.yaml',
	]

	def setUp(self):
		self.user_data = {
			"email": "testuser1@app.com",
			"username": "testuser1@app.com",
			"password": "Password1",
		}
		self.user = get_user_model().objects.get(username=self.user_data['username'])
		self.client.authenticate(self.user)

		self.questionnaire_data = {
			'id': None,
			'title': 'Interview questions'
		}

		self.questions_data = [
			# 0
			{
				'id': None,
				'text': 'Do you have experience with GraphQL?',
				'answer_type': 'SHORT_ANSWER'
			},
			# 1
			{
				'id': None,
				'text': 'How many years you are working as software engineer?',
				'answer_type': 'SHORT_ANSWER'
			},
			# 2 - Will be deleted for test
			{
				'id': None,
				'text': 'What is difference between TCP and UDP protocols?',
				'answer_type': 'SHORT_ANSWER'
			},
			# 3
			{
				'id': None,
				'text': 'Which tech stack you will choose for new application?',
				'answer_type': 'SHORT_ANSWER'
			}
		]
		self.questions_data_index_for_delete = 2
		self.questions_data_after_delete = \
			self.questions_data[:self.questions_data_index_for_delete] \
			+ self.questions_data[self.questions_data_index_for_delete+1:]

	def tearDown(self):
		pass

	def create_questionnaire(self, title=None):
		executed = self.client.execute('''
		mutation CreateQuestionnaire(
			$title: String!
		) {
			createQuestionnaire(
				title: $title
			) { %s }
		}
		''' % requested_data, {
			'title': title
		})

		questionnaire = executed.data['createQuestionnaire']['questionnaire']
		return questionnaire

	def create_question(self, text=None, answer_type=None, questionnaire_id=None):
		executed = self.client.execute('''
		mutation CreateQuestion(
			$questionnaireId: Int!,
			$text: String!,
			$answerType: AnswerType!,
		) {
			createQuestion(
				questionnaireId: $questionnaireId,
				text: $text,
				answerType: $answerType,
			) { %s }
		}
		''' % requested_data, {
			'questionnaireId': questionnaire_id,
			'text': text,
			'answerType': answer_type,
		})
		questionnaire = executed.data['createQuestion']['questionnaire']
		return questionnaire

	def delete_question(self, questionnaire_id=None, question_id=None):
		executed = self.client.execute('''
		mutation DeleteQuestion(
			$questionnaireId: Int!,
			$questionId: Int!,
		) {
			deleteQuestion(
				questionnaireId: $questionnaireId,
				questionId: $questionId,
			) { %s }
		}
		''' % requested_data, {
			'questionnaireId': questionnaire_id,
			'questionId': question_id,
		})
		questionnaire = executed.data['deleteQuestion']['questionnaire']
		return questionnaire

	def reorder_questions(self, questionnaire_id=None, ordered_question_ids=None):
		executed = self.client.execute('''
		mutation ReorderQuestions(
			$questionnaireId: Int!,
			$orderedQuestionIds: [Int]!,
		) {
			reorderQuestions(
				questionnaireId: $questionnaireId,
				orderedQuestionIds: $orderedQuestionIds,
			) { %s }
		}
		''' % requested_data, {
			'questionnaireId': questionnaire_id,
			'orderedQuestionIds': ordered_question_ids,
		})
		questionnaire = executed.data['reorderQuestions']['questionnaire']
		return questionnaire

	def test_Questionnaire(self):
		# 1. Create Questionnaire
		questionnaire = self.create_questionnaire(title=self.questionnaire_data['title'])
		questionnaire_id = questionnaire['id']

		self.questionnaire_data['id'] = questionnaire_id
		assert questionnaire['id'] == self.questionnaire_data['id']
		assert questionnaire['title'] == self.questionnaire_data['title']
		assert questionnaire['userCreator']['email'] == self.user_data['email']
		assert questionnaire['orderedQuestionIds'] == []
		assert questionnaire['questionSet'] == []

		# 2. Create Questions in Questionnaire
		ordered_question_ids = []
		for index, question_data in enumerate(self.questions_data):
			questionnaire = self.create_question(
				text=question_data['text'],
				answer_type=question_data['answer_type'],
				questionnaire_id=self.questionnaire_data['id']
			)

			question = questionnaire['questionSet'][index]
			question_id = question['id']

			ordered_question_ids.append(question_id)
			assert questionnaire['orderedQuestionIds'] == ordered_question_ids

			self.questions_data[index]['id'] = question_id
			assert question['text'] == self.questions_data[index]['text']
			assert question['answerType'] == self.questions_data[index]['answer_type']

		assert len(questionnaire['questionSet']) == len(self.questions_data)

		# 3. Delete Question from Questionnaire
		questionnaire_after_delete = self.delete_question(
			question_id=self.questions_data[self.questions_data_index_for_delete]['id'],
			questionnaire_id=self.questionnaire_data['id']
		)

		assert questionnaire_after_delete['id'] == self.questionnaire_data['id']
		assert questionnaire_after_delete['title'] == self.questionnaire_data['title']
		assert questionnaire_after_delete['userCreator']['email'] == self.user_data['email']

		expected_ordered_question_ids_after_delete = ordered_question_ids.copy()
		expected_ordered_question_ids_after_delete.remove(
			self.questions_data[self.questions_data_index_for_delete]['id']
		)

		assert questionnaire_after_delete['orderedQuestionIds'] == expected_ordered_question_ids_after_delete
		assert len(questionnaire_after_delete['questionSet']) == len(self.questions_data_after_delete)

		for question in questionnaire_after_delete['questionSet']:
			assert question['id'] in expected_ordered_question_ids_after_delete

		# 4. Reorder Questions in Questionnaire
		ordered_question_ids_before_reorder = expected_ordered_question_ids_after_delete
		questionnaire_before_reorder = questionnaire_after_delete

		expected_ordered_question_ids_after_reorder = ordered_question_ids_before_reorder.copy()
		expected_ordered_question_ids_after_reorder[0], expected_ordered_question_ids_after_reorder[1] = \
			expected_ordered_question_ids_after_reorder[1], expected_ordered_question_ids_after_reorder[0]
		questionnaire_after_reorder = self.reorder_questions(
			questionnaire_id=self.questionnaire_data['id'],
			ordered_question_ids=expected_ordered_question_ids_after_reorder
		)

		assert questionnaire_before_reorder['orderedQuestionIds'] == ordered_question_ids_before_reorder
		assert questionnaire_after_reorder['orderedQuestionIds'] == expected_ordered_question_ids_after_reorder

		assert questionnaire_before_reorder['questionSet'] == questionnaire_after_reorder['questionSet']
