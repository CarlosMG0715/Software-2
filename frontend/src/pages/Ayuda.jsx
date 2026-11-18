const FAQ = [
  ["¿Mi reseña es realmente anónima?", "Sí. Tu identidad se guarda solo como un código irreversible y nunca se muestra a docentes, moderadores ni otros estudiantes."],
  ["¿Cuántas reseñas puedo escribir por docente?", "Una por docente, materia y periodo. Puedes editarla o eliminarla cuando quieras."],
  ["¿Qué pasa si reportan una reseña?", "Con 5 reportes de usuarios distintos se oculta y un moderador la revisa: puede aprobarla, rechazarla o eliminarla."],
  ["¿Cómo se califica?", "Claridad, exigencia y puntualidad de 1 a 5; la escala se explica en cada criterio del formulario."],
  ["¿Qué datos personales se tratan?", "Tu correo institucional, bajo la Ley 1581 de 2012, solo para autenticarte."],
  ["Olvidé mi contraseña", "Usa «Olvidé mi clave» en la pantalla de ingreso: recibirás un token temporal."],
];

export default function Ayuda() {
  return (
    <>
      <h1>Ayuda y preguntas frecuentes</h1>
      {FAQ.map(([q, a]) => (
        <details key={q} className="tarjeta"><summary>{q}</summary><p>{a}</p></details>
      ))}
    </>
  );
}