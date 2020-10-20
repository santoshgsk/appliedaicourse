
function getPredictions(endpoint, formData) {
    
  var options = {
    'method' : 'post',
    'contentType': 'application/json',
    'payload' : JSON.stringify(formData)
  };
  
  Logger.log(formData);
  
  var res = UrlFetchApp.fetch(endpoint, options);
  
  var predictions = JSON.parse(JSON.parse(res.getContentText()));
  
  Logger.log(predictions.result[0]);
  
  return predictions.result;
  
}

function getData(endpoint) {
  
  var sheet = SpreadsheetApp.getActiveSheet();  
  
  var values = sheet.getDataRange().getValues();
  
  var header = values.shift();
  
  Logger.log(header);
  
  var lastrow = sheet.getLastRow();
  
  var lastcolumn = sheet.getLastColumn();
  
  var predictions = [['predictions']];
  
  values.forEach(function(row) {
    
    formData = {}
    for(var i = 0; i < header.length; i++)
    {
      formData[header[i]] = row[i];
    }
   
    formDict = {"data": [formData]};
        
    predictions.push(getPredictions(endpoint, formDict));
    
  })
  
  sheet.getRange(1, lastcolumn+1, lastrow, 1).setValues(predictions);
    
}

function showPopup() {
  
  var ui = SpreadsheetApp.getUi();
  
  var prompt = ui.prompt("Azure AutoML Endpoint", "Enter the endpoint url of the AutoML model", ui.ButtonSet.OK);
  
  var endpoint = prompt.getResponseText();
  
  Logger.log(endpoint.length);
  
  if (endpoint.length > 0)
  {
    getData(endpoint)
  }
}


function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Azure AutoML')
      .addItem('Get Predictions', 'showPopup')
      .addToUi();
  
  
}
