class DesmosDrawer {
  constructor() {
    this.calculator = window.Calc
    this.count = 0
    this.otherId = []
  }
  
  add(info) {
    let { expr, color } = info
    let id = `expr${this.count++}`
    
    this.calculator.setExpression({ latex: expr, id, color })
  }
  
  addAll = infos => infos.forEach(this.add.bind(this))
  
  remove = id => this.calculator.removeExpression({id})
  
  clear() {
    while (this.count--) this.remove(`expr${this.count}`)
  }
}

let c = new DesmosDrawer()
let drawIt = url => Desmos.$.get(url, data => c.addAll(JSON.parse(data).map(expr => {return {expr}})))
