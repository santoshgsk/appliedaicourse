
function getPredictions(endpoint, formData) {
    
  var options = {
    'method' : 'post',
    'contentType': 'application/json',
    'payload' : JSON.stringify(formData)
  };
    
  var res = UrlFetchApp.fetch(endpoint, options);
  
  var predictions = JSON.parse(JSON.parse(res.getContentText()));
  
  if ( 'result' in predictions)
  {
    return predictions.result;
  } 
  if ( 'forecast' in predictions)
  {
    return predictions.forecast;
  }
  
  
}

function getData(endpoint, data_types) {
  
  var sheet = SpreadsheetApp.getActiveSheet();  
  
  var values = sheet.getDataRange().getValues();
  
  var header = values.shift();
  
  for(var i = 0; i<header.length; i++)
  {
    var types = data_types[header[i]];
    if (types['type'] === 'string')
    {
      sheet.getRange(2, i+1, sheet.getLastRow(), 1).setNumberFormat("@");
    }
    if (types['type'] === 'integer')
    {
      
      var range = sheet.getRange(2, i+1, sheet.getLastRow()-1, 1);
      
      range.setNumberFormat("0");
      var data = range.getValues();
      range.setValues(
        data.map( function(row)
           {
             return row.map( function(cell) {
               return cell === "" ? "NaN" : cell;
             }
             );
           }
        )
      );
    }
    if (types['type'] === 'number')
    {
      var range = sheet.getRange(2, i+1, sheet.getLastRow()-1, 1);
      
      range.setNumberFormat("0.000000000");
      var data = range.getValues();
      range.setValues(
        data.map( function(row)
           {
             return row.map( function(cell) {
               return cell === "" ? "NaN" : cell;
             }
             );
           }
        )
      );
      
    }
  }
    
  var lastrow = sheet.getLastRow();
  
  var lastcolumn = sheet.getLastColumn();
  
  var predictions = [];
  
  var dataArray = [];
  
  var values = sheet.getRange(2, 1, sheet.getLastRow()-1, sheet.getLastColumn()).getValues();
  
//  sheet.getRange(1, lastcolumn+1, 1, 1).setValues([['predictions']]);
  
//  var preds_so_far = 1

  values.forEach(function(row) {
    
    formData = {};
    
    for(var i = 0; i < header.length; i++)
    {      
      formData[header[i]] = row[i];
    }
   
    dataArray.push(formData);
    
    if (dataArray.length >= 1000 ){
      
      formDict = {"data" : dataArray};
      predictions = predictions.concat(getPredictions(endpoint, formDict));
      
      
      dataArray = [];
    }
  })
  
  Logger.log(dataArray);
  if (dataArray.length > 0) {
    formDict = {"data" : dataArray};
    predictions = predictions.concat(getPredictions(endpoint, formDict));
  }
  
  log_preds = [['predictions']]
  predictions.forEach(function(pred) {
  
    log_preds.push([pred]);
  }
  )
  
  Logger.log(log_preds);
  sheet.getRange(1, lastcolumn+1, lastrow, 1).setValues(log_preds);
    
}

function getDataTypes(endpoint) {
  
  var swagger = endpoint.replace("score", "swagger.json");
  
  var res = UrlFetchApp.fetch(swagger);
  
  var swagger_res = JSON.parse(res);
  
  var data_types = swagger_res['definitions']['ServiceInput']['properties']['data']['items']['properties'];

  return data_types;
  
}

function showPopup() {
  
  var ui = SpreadsheetApp.getUi();
  
  var prompt = ui.prompt("Azure AutoML Endpoint", "Check this blog for instructions https://santoshgsk.com/azure-automl-inference-addon/", ui.ButtonSet.OK);
  
  var endpoint = prompt.getResponseText();
  
  var data_types = getDataTypes(endpoint);
  
//  Logger.log(endpoint.length);
  
  if (endpoint.length > 0)
  {
    getData(endpoint, data_types)
  }
}


function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Azure AutoML')
      .addItem('Get Predictions', 'showPopup')
      .addToUi();
  
}
