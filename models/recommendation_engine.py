# recommendation_engine.py

import json
from sklearn.metrics.pairwise import cosine_similarity
from models.pretrained_nlp import PretrainedNLP

class RecommendationEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the recommendation engine with a pretrained NLP model
        and load research trends data.
        """
        self.nlp_model = PretrainedNLP(model_name=model_name)
        self.research_trends = self.load_research_trends()

    def load_research_trends(self, file_path="data/research_trends.json"):
        """
        Load research trends from a JSON file.
        :param file_path: Path to JSON file with research topics and fields.
        :return: List of dictionaries with 'field' and 'topic' keys.
        """
        with open(file_path, 'r') as f:
            research_trends = json.load(f)
        # Generate embeddings for each topic in research trends
        for topic in research_trends:
            topic['embedding'] = self.nlp_model.get_embedding(topic['topic'])
        return research_trends

    def calculate_feasibility(self, topic, user_skills, available_time):
        """
        Calculate a feasibility score based on the topic requirements and user input.
        :param topic: Dictionary containing topic details and requirements.
        :param user_skills: List of skills the user has.
        :param available_time: The time (in months) the user can dedicate to research.
        :return: Feasibility score (0 to 1 scale).
        """
        # Define weights for each criterion
        skill_weight = 0.4
        time_weight = 0.3
        resource_weight = 0.3
        
        # Calculate skill match
        required_skills = topic.get("required_resources", [])
        skill_match = sum([1 for skill in user_skills if skill in required_skills]) / len(required_skills) if required_skills else 1
        
        # Calculate time feasibility
        time_match = 1 if available_time >= topic.get("estimated_time", 0) else available_time / topic.get("estimated_time", 1)
        
        # Calculate resource feasibility (for simplicity, assume a match if the user has at least one required resource)
        resource_match = skill_match if any(skill in required_skills for skill in user_skills) else 0

        # Overall feasibility score (weighted)
        feasibility_score = (skill_weight * skill_match) + (time_weight * time_match) + (resource_weight * resource_match)
        return feasibility_score

    def match_advisors(self, topic_field):
        """
        Match advisors based on the field of the selected topic.
        :param topic_field: Field of the research topic.
        :return: List of advisors in the same field.
        """
        with open("data/advisors.json", "r") as f:
            advisors = json.load(f)
        
        # Filter advisors with expertise in the topic's field
        matching_advisors = [advisor for advisor in advisors if topic_field == advisor["field"]]
        return matching_advisors

    def recommend_topics(self, user_input, user_skills, available_time, top_n=3):
        """
        Recommend PhD topics based on user's input and calculate feasibility.
        :param user_input: String, user-provided input on interests.
        :param user_skills: List of user's skills.
        :param available_time: The time (in months) the user has for research.
        :param top_n: Number of top recommendations to return.
        :return: List of recommended topics with feasibility scores.
        """
        user_embedding = self.nlp_model.get_embedding(user_input)
        
        similarities = []
        for topic in self.research_trends:
            similarity = cosine_similarity([user_embedding], [topic['embedding']])[0][0]
            feasibility_score = self.calculate_feasibility(topic, user_skills, available_time)
            similarities.append((topic, similarity, feasibility_score))
        
        # Sort by similarity and then feasibility score
        top_recommendations = sorted(similarities, key=lambda x: (x[1], x[2]), reverse=True)[:top_n]
        
        # Return only the topic and scores
        return [{"topic": rec[0]["topic"], "field": rec[0]["field"], "similarity": rec[1], "feasibility": rec[2]} for rec in top_recommendations]

# Example usage
if __name__ == "__main__":
    # Initialize the recommendation engine
    engine = RecommendationEngine()
    
    # User input for testing
    user_input = "I'm interested in neural networks and how they can be applied in healthcare."
    user_skills = ["NLP tools", "Python", "Data Analysis"]
    available_time = 18  # in months

    # Get recommendations
    recommendations = engine.recommend_topics(user_input, user_skills, available_time)
    for i, rec in enumerate(recommendations, start=1):
        print(f"Recommendation {i}: Field - {rec['field']}, Topic - {rec['topic']}")
        print(f"  Similarity Score: {rec['similarity']:.2f}, Feasibility Score: {rec['feasibility']:.2f}")
        
        # Advisor Matching
        advisors = engine.match_advisors(rec['field'])
        print("  Matching Advisors:")
        for advisor in advisors:
            print(f"    - {advisor['name']}, Expertise: {advisor['expertise']}")
