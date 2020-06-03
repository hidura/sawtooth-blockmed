var m = require("mithril")
var Patient = require("../models/Patient")
var idcartoptions=[
                m("option", "Select IDCARD TYPE",{
                    oninput: m.withAttr("value", function(value) {Patient.current.idcardtype = 0}),
                    value: Patient.current.idcardtype
                }),
                m("option", "RNC",{
                    oninput: m.withAttr("value", function(value) {Patient.current.idcardtype = 1}),
                    value: Patient.current.idcardtype
                }),
                m("option", "Cedula",{
                    oninput: m.withAttr("value", function(value) {Patient.current.idcardtype = 2}),
                    value: Patient.current.idcardtype
                }),
                m("option", "Passport",{
                    oninput: m.withAttr("value", function(value) {Patient.current.idcardtype = 3}),
                    value: Patient.current.idcardtype
                })
            ]
module.exports = {
    view: function() {
        return m("form", {
                onsubmit: function(e) {
                    e.preventDefault()
                    Patient.register()
                }
            }, [
            m("label.label", "First name"),
            m("input.input[type=text][placeholder=First name]", {
                oninput: m.withAttr("value", function(value) {Patient.current.name = value}),
                value: Patient.current.name
            }),
            m("label.label", "Last name"),
            m("input.input[placeholder=Last name]", {
                oninput: m.withAttr("value", function(value) {Patient.current.surname = value}),
                value: Patient.current.surname
            }),
            m("label.label", "IDCard/Passport"),
            m("input.input[placeholder=IDCard/Passport]", {
                oninput: m.withAttr("value", function(value) {Patient.current.idcard = value}),
                value: Patient.current.idcard
            }),
            m('select', { onchange : function(){ alert('this') }},[
              {"Select option ":0, "RNC":1, "CEDULA":2, "PASSPORT":3}.map(function(d, i){
                return m('option', { value : d, innerHTML : 1 })

              })
            ]),

            m("button.button[type=submit]", "Register"),
            m("label.error", Patient.error)
        ])
    }
}