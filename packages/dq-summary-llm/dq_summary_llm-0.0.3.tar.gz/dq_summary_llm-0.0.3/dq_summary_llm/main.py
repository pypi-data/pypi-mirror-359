import openai
import pandas as pd

class DataQualitySummery:
    def __init__(self,api_key: str, model:str="azure.gpt-4.1", temprature: float=0.7, max_token: int=1000, base_url: str=None):
        self.api_key= api_key
        self.base_url= base_url
        self.model= model
        self.temprature= temprature
        self.max_token= max_token

    def create_connection(self):
        try:
            client=None
            if self.base_url is not None and 'pwc' in self.base_url:
                # print(self.api_key,self.base_url)
                client= openai.OpenAI(
                        api_key=self.api_key,
                        base_url=self.base_url
                    )
                if client:
                        return client
                else:
                        return "Connection establish unsuccessful"
            else:
                client= openai.OpenAI(
                        api_key=self.api_key,
                    )
                if client:
                        return client
                else:
                        return "Connection establish unsuccessful"
                
        except Exception as e:
            return f"Error: {e}"
        
    def data_quality_details(self, data: pd.DataFrame, response:str=None)-> str:
        try:
            system_prompt= """
            You are an expert in data quality and data analytics who understand data impact on business
            Based on Gartener Data Quality Metrics, please assess dataset and return a report that includes:
            - Defination for each metrics (Completeness, Uniqueness, Accuracy, Consistency, Timeleness, Validity)
            - Score (out of 100) per matric (or N/A if not applicable)
            - Area for Imporvement per metric
            - Summery table
            - Overall data quality score
            Here is the dataset:
            """+(data.to_string(index=False)[:3000] if data is not None else '') # truncate to avoid token limit
            client= self.create_connection()
            if data is not None:
                message= [{"role":"user", "content": system_prompt}]
                llm_response= client.chat.completions.create(
                    model=self.model,
                    messages= message,
                    temperature= self.temprature,
                    max_tokens= self.max_token
                )

                gratner_output= llm_response.choices[0].message.content
                # print(gratner_output)
                return gratner_output
        except Exception as e:
             return f"Error {e}"
    
    def data_quality_summery(self, response):

        try:
             
            sys_promt=  f"""
            Based on the user response summerise the content and present it within 150 words {response}
            """

            client= self.create_connection()
            if response is not None:
                message= [{"role":"user", "content": sys_promt}]
                llm_response= client.chat.completions.create(
                    model=self.model,
                    messages= message,
                    temperature= self.temprature,
                    max_tokens= self.max_token
                )

                gratner_output_summery= llm_response.choices[0].message.content
                # print(gratner_output_summery)
                return gratner_output_summery
        except Exception as e:
             return f"Error: {e}"
        
    def data_explainer(self, data: pd.DataFrame, 
                       user_prompt: str= None,
                       sample_size: int=10)-> str:
        try:
            schema_parts=[]
            data_length= data.shape[0]
            sample_sizes=min(sample_size,data_length)
            for col in data.columns:
                dtype=str(data[col].dtype)
                sample_values= data[col].astype(str).unique()[:sample_sizes]
                sample_str=', '.join(sample_values)
                schema_parts.append(f"- {col} ({dtype}): eg., {sample_str}")
            schema_str= "\n" .join(schema_parts)
                
            sys_promt= f"""
                You are an expert data scientist and master data storyteller
                - Here are the {schema_str}
                - Describe what the column likely represents what is the data is trying to explain 
                - Provide concise, human-readable explanation
                """
            message=[]
            client= self.create_connection()
            if user_prompt is None:
                    message.append({"role":"user", "content": sys_promt})
                    llm_response= client.chat.completions.create(
                        model=self.model,
                        messages= message,
                        temperature= self.temprature,
                        max_tokens= self.max_token
                    )

                    data_explaipner= llm_response.choices[0].message.content
                    # print(gratner_output_summery)
                    return data_explaipner
            else:
                message.append({"role":"system", "content": sys_promt})
                message.append({"role":"user", "content": user_prompt})
                llm_response= client.chat.completions.create(
                        model=self.model,
                        messages= message,
                        temperature= self.temprature,
                        max_tokens= self.max_token
                    )

                data_explaipner= llm_response.choices[0].message.content
                    # print(gratner_output_summery)
                return data_explaipner 
             
        
        except Exception as e:
             return f"Error: {e}"
             
         
        
             
        
        



        
    