// JavaScript Document

function check()
{
	var fn=document.forms["forma"]["firstname"].value;
	var pw=document.forms["forma"]["passw"].value;
	
	if (fn.length>20)
	{
		alert("Поле \"Логин\" не может быть длиннее 20 символов!");
		return false;
	}
	
	if (fn==null || fn=="" || pw==null || pw=="")
	{
		alert("Поля \"Логин\" или \"Пароль\" не заполнены!");
                return false;
	}	
	
};