﻿
&НаКлиенте
Процедура ПриОткрытии(Отказ)    
	
	СерверКамеры = "localhost";
	Порт = "5000";
	КартинкаКамеры = СтрШаблон("http://%1:%2", СерверКамеры, Формат(Порт, "ЧРД="""""));
	
КонецПроцедуры

&НаКлиенте
Процедура Реквизит1ДокументСформирован(Элемент)
	//// Вставить содержимое обработчика.
	//	Реквизит1="http://localhost:5000/";
	//	ДокументHTML = Элементы.Реквизит1.Документ;
	//    //ДокументHTML.URL="http://localhost:5000/"   ;
	//	АдресHTML = ДокументHTML.URL;

	//	Текст_HTML = ДокументHTML.documentElement.innerHTML;
КонецПроцедуры

&НаКлиенте
Процедура АдресКамерыПриИзменении(Элемент)
	КартинкаКамеры=АдресКамеры
КонецПроцедуры

&НаКлиенте
Процедура НачатьПоискКода(Команда)
	
	
	Ответ = КомандаКамеры(МетодНовоеСканирование());
	
	Если Ответ.КодСостояния <> 200 Тогда
		Сообщить(Ответ.КодСостояния);
	КонецЕсли;
	
	Элементы.НачатьПоискКода.Доступность = Ложь;
	ЭтаФорма.ТекущийЭлемент = Элементы.вводКода;
	//ПодключитьОбработчикОжидания("ЖдатьЧтенияКода",0.1, Истина);
	
КонецПроцедуры

&НаКлиенте
Процедура ЖдатьЧтенияКода()
	
	уин = "";
	Попыток = 20;
	счПопытки = 0;
	тСтарт = ТекущаяУниверсальнаяДатаВМиллисекундах();
	//рез = КомандаКамеры(МетодСтарт());
	Пока счПопытки < Попыток Цикл
		Состояние("Жду чтения кода", счПопытки/Попыток*100);
		
		счПопытки = счПопытки + 1;
		рез = КомандаКамеры(МетодПолучитьУИН());
		Если рез.КодСостояния <> 200 Тогда
			Сообщить(рез.КодСостояния);
			Прервать;
		КонецЕсли;
		
		уин = УинИзОтветаЗапроса(рез);
		Если не ПустаяСтрока(уин) Тогда
			рез = КомандаКамеры(МетодПодтвердитьПолучениеУИН());
			СчитанныйКод = уин;
			Прервать;
		КонецЕсли;
		
		Пока ТекущаяУниверсальнаяДатаВМиллисекундах() < тСтарт + 100 Цикл
		КонецЦикла;
			
	КонецЦикла;  
	
	Элементы.НачатьПоискКода.Доступность = Истина;
	ОтключитьОбработчикОжидания("ЖдатьЧтенияКода");
	
КонецПроцедуры

&НаКлиенте
Функция МетодСтарт()

	возврат Новый Структура(
	"Адрес, ТипМетода"
		,"/video_feed"
		, "GET");
	
КонецФункции


&НаКлиенте
Функция МетодПолучитьУИН()
	
	возврат Новый Структура(
	"Адрес, ТипМетода"
		,"/lastreadcode"
		, "GET");
	
КонецФункции

&НаКлиенте
Функция МетодПодтвердитьПолучениеУИН()
	
	возврат Новый Структура(
	 	"Адрес, ТипМетода"  
			,"/stopscan"
	 		, "GET");
	
КонецФункции                     

&НаКлиенте
Функция МетодНовоеСканирование()
	
	возврат Новый Структура(
	 	"Адрес, ТипМетода" 
			,"/newscan"
	 		, "GET");
	
КонецФункции

&НаКлиенте
Функция УинИзОтветаЗапроса(Ответ) 
	
	чтJSON = Новый ЧтениеJSON;
	чтJSON.УстановитьСтроку(Ответ.ПолучитьТелоКакСтроку());
	ПрочитатьJSON(чтJSON);
	дт = чтJSON.Закрыть();	
	
	Если дт = Неопределено Тогда
		Возврат "";
	КонецЕсли;
	
	Если дт.Свойство("uin") Тогда
		возврат дт.uin;
	КонецЕсли;         
	
	Возврат "";
КонецФункции

&НаКлиенте
Функция КомандаКамеры(ПараметрыЗапроса)
	Попытка	
		Соединение = Новый HTTPСоединение(СерверКамеры, Число(Порт));
		Запрос = Новый HTTPЗапрос;
		Запрос.АдресРесурса = ПараметрыЗапроса.Адрес;
	Исключение
		Сообщить(ОписаниеОшибки());
	КонецПопытки;
	Возврат Соединение.ВызватьHTTPМетод(ПараметрыЗапроса.ТипМетода,Запрос);
	
КонецФункции

&НаКлиенте
Процедура ПрерватьПоиск(Команда)    
	
	Элементы.НачатьПоискКода.Доступность = Истина;
	//ОтключитьОбработчикОжидания("ЖдатьЧтенияКода");
	рез = КомандаКамеры(МетодПодтвердитьПолучениеУИН());
КонецПроцедуры

&НаКлиенте
Процедура вводКодаОкончаниеВводаТекста(Элемент, Текст, ДанныеВыбора, ПараметрыПолученияДанных, СтандартнаяОбработка)
	Элементы.НачатьПоискКода.Доступность = Истина;    
	ПрерватьПоиск(Неопределено);
	ОтсканированныеКоды.Добавить(Текст);
КонецПроцедуры
