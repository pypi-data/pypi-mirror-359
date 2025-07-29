from datetime import datetime

from database_mysql_local.generic_crud_ml import GenericCRUDML
from language_remote.lang_code import LangCode
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.MetaLogger import MetaLogger
from user_context_remote.user_context import UserContext
from .email_address_constants import EmailAddressConstants


object1 = {
   'component_id': EmailAddressConstants.EMAIL_ADDRESS_LOCAL_PYTHON_COMPONENT_ID,
   'component_name': EmailAddressConstants.EMAIL_ADDRESS_LOCAL_PYTHON_COMPONENT_NAME,
   'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
   'developer_email': "idan.a@circ.zone"
}



class EmailAddressesLocal(GenericCRUDML, metaclass=MetaLogger, object=object1):
   # TODO Where shall we link email-address_id to person, contact, profile ...?
   # Can we create a generic function for that in GenericCRUD and use it multiple times
   # in https://github.com/circles-zone/email-address-local-python-package
   def __init__(self, is_test_data: bool = False) -> None:
       super().__init__(default_schema_name = EmailAddressConstants.EMAIL_ADDRESS_SCHEMA_NAME,
                        default_table_name = EmailAddressConstants.EMAIL_ADDRESS_TABLE_NAME,
                        default_view_table_name = EmailAddressConstants.EMAIL_ADDRESS_VIEW_TABLE_NAME,
                        default_ml_table_name = EmailAddressConstants.EMAIL_ADDRESS_ML_TABLE_NAME,
                        default_ml_view_table_name = EmailAddressConstants.EMAIL_ADDRESS_ML_VIEW_TABLE_NAME,
                        default_column_name = EmailAddressConstants.EMAIL_ADDRESS_ID_COLLUMN_NAME,
                        is_test_data=is_test_data)
       self.user_context = UserContext()
       


   # title is multi-language
   # name is internal only English
   def insert(self, *,  # noqa
              email_address_str: str, name: str = None, lang_code: LangCode, title: str, data_dict: dict = None) -> int or None:
       email_address_dict = data_dict or {}
       email_address_dict[EmailAddressConstants.EMAIL_ADDRESS_COLUMN_NAME] = email_address_str
       if name is not None:
        email_address_dict["name"] = name
       email_address_id = super().insert(data_dict=email_address_dict)

       email_address_ml_dict = {
           "email_address_id": email_address_id,
           "lang_code": lang_code.value,
           "title": title
       }
       super().insert(table_name=EmailAddressConstants.EMAIL_ADDRESS_ML_TABLE_NAME, data_dict=email_address_ml_dict)

       return email_address_id

   def update_email_address(self, email_address_id: int, new_email_address_str: str) -> None:
       email_address_dict = {EmailAddressConstants.EMAIL_ADDRESS_COLUMN_NAME: new_email_address_str}
       self.update_by_column_and_value(column_value=email_address_id, data_dict=email_address_dict)

   def delete(self, email_address_id: int) -> None:
       self.delete_by_column_and_value(column_value=email_address_id)


   def get_email_address_str_by_email_address_id(self, email_address_id: int) -> str:
       assert isinstance(email_address_id, int)
       email_address_str = self.select_one_value_by_column_and_value(
           schema_name = EmailAddressConstants.EMAIL_ADDRESS_SCHEMA_NAME,
           column_name = EmailAddressConstants.EMAIL_ADDRESS_ID_COLLUMN_NAME,
           view_table_name=EmailAddressConstants.EMAIL_ADDRESS_VIEW_TABLE_NAME,
           select_clause_value=EmailAddressConstants.EMAIL_ADDRESS_COLUMN_NAME, column_value=email_address_id)

       return email_address_str

   def get_email_address_id_by_email_address_str(self, email_address_str: str) -> int:
       assert isinstance(email_address_str, str)
       email_address_id = self.select_one_value_by_column_and_value(
           select_clause_value=EmailAddressConstants.EMAIL_ADDRESS_ID_COLLUMN_NAME,
           column_name=EmailAddressConstants.EMAIL_ADDRESS_COLUMN_NAME, column_value=email_address_str)
       return email_address_id

   def verify_email_address_str(self, email_address_str: str) -> None:
       """verify_email_address executed by SmartLink/Action"""
       assert isinstance(email_address_str, str)
       self.update_by_column_and_value(column_name=EmailAddressConstants.EMAIL_ADDRESS_COLUMN_NAME,
                                       column_value=email_address_str, data_dict={"is_verified": True})



   def get_domain_id_from_email_address_str(self, email_address_str: str) -> int:
       email_address_domain = email_address_str.split("@", 1)[1]
       internet_domain_id = self.select_one_value_by_column_and_value(
           select_clause_value="internet_domain_id",
           schema_name="internet_domain",
           view_table_name="internet_domain_view",
           column_name="domain",
           column_value=email_address_domain)

       return internet_domain_id

   def get_mailbox_name_str_from_email_address_str(self, email_address_str: str) -> str:
       mailbox_name_str = email_address_str.split("@", 1)[0]
       return mailbox_name_str
  
   def update_database_with_mailbox_name_str(self,email_address_str: str) -> None:
       mailbox_name_str = self.get_mailbox_name_str_from_email_address_str(email_address_str =
                                                                           email_address_str)
      
       self.update_by_column_and_value(schema_name="email_address",
                                        table_name="email_address_table",
                                        column_name="email_address",
                                        column_value=email_address_str,
                                        data_dict={"username": mailbox_name_str}
                                        )


   @staticmethod
   def get_test_email_address() -> str:
       """Generates a generic email_address_str address.
       For example: email2023-12-24 23:29:43.269076@test.com"""
       """Generates a generic email address.
       For example: email20231224232943@test.com"""
       test_email_address = "email" + str(datetime.now()) + "@test.com"
       return test_email_address

   def get_test_email_address_id(self) -> int:
       return super().get_test_entity_id(entity_name="email_address",
                                         insert_function=self.insert,
                                         insert_kwargs={"email_address_str": self.get_test_email_address(),
                                                        "lang_code": LangCode.ENGLISH,
                                                        "name": "test"})
