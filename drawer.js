class DesmosDrawer {
  constructor() {
    this.calculator = Desmos.GraphingCalculator(
      document.getElementsByClassName('dcg-container')[0]
    )
    this.count = 0
    this.otherId = []
  }
  
  add(info) {
    let { expr, color, id } = info
    id = (_ => {this.otherId.push(id); return id})() || `expr${this.count++}`
    
    this.calculator.setExpression({ latex: expr, id, color })
  }
  
  addAll = infos => infos.forEach(this.add.bind(this))
  
  remove = id => this.calculator.removeExpression({id})
  removeAll = ids => ids.forEach(this.remove.bind(this))
  
  clear() {
    this.removeAll(Array(this.count).fill(0).map((_, idx) => `expr${idx}`))
    this.removeAll(this.otherId)
    this.count = 0
    this.otherId = []
  }
}

let c = new DesmosDrawer()
drawIt = url => Desmos.$.get(url, data => c.addAll(JSON.parse(data).map(expr => {return {expr}})))
