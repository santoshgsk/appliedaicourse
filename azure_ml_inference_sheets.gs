var endpoint = 'http://53730935-2685-415a-99f7-9d2e148b2624.eastus.azurecontainer.io/score'


function getPredictions(formData) {
    
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

function getData() {
  
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
        
    predictions.push(getPredictions(formDict));
    
  })
  
  sheet.getRange(1, lastcolumn+1, lastrow, 1).setValues(predictions);
    
}












