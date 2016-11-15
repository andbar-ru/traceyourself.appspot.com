$.tablesorter.addParser({
  id: "windDirection",
  is: function(s) {
    return /штиль|север|северо-северо-восток|северо-восток|востоко-северо-восток|восток|востоко-юго-восток|юго-восток|юго-юго-восток|юг|юго-юго-запад|юго-запад|западо-юго-запад|запад|западо-северо-запад|северо-запад|северо-северо-запад/.test(s);
  },
  format: function(s) {
    switch (s) {
      case 'штиль': return -1
      case 'север': return 0
      case 'северо-северо-восток': return 1
      case 'северо-восток': return 2
      case 'востоко-северо-восток': return 3
      case 'восток': return 4
      case 'востоко-юго-восток': return 5
      case 'юго-восток': return 6
      case 'юго-юго-восток': return 7
      case 'юг': return 8
      case 'юго-юго-запад': return 9
      case 'юго-запад': return 10
      case 'западо-юго-запад': return 11
      case 'запад': return 12
      case 'западо-северо-запад': return 13
      case 'северо-запад': return 14
      case 'северо-северо-запад': return 15
      default: return 16
    }
  },
  type: 'numeric'
});

$.tablesorter.addParser({
  id: "moonPhase",
  is: function(s) {
    return /новолуние|растущий серп|первая четверть|растущая луна|полнолуние|убывающая луна|последняя четверть|убывающий серп/.test(s);
  },
  format: function(s) {
    switch (s) {
      case 'новолуние': return 0
      case 'растущий серп': return 1
      case 'первая четверть': return 2
      case 'растущая луна': return 3
      case 'полнолуние': return 4
      case 'убывающая луна': return 5
      case 'последняя четверть': return 6
      case 'убывающий серп': return 7
      default: return 8
    }
  },
  type: 'numeric'
});

