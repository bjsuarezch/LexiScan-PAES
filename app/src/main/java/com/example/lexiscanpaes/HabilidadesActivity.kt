package com.example.lexiscanpaes

import android.os.Bundle
import android.os.CountDownTimer
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject

class HabilidadesActivity : AppCompatActivity() {

    private lateinit var tvSkillName: TextView
    private lateinit var pbMastery: ProgressBar
    private lateinit var tvSinclairText: TextView
    private lateinit var tvQuestion: TextView
    private lateinit var rgOptions: RadioGroup
    private lateinit var btnRespond: Button
    private lateinit var tvFeedbackCoT: TextView
    private lateinit var btnVoiceTutor: ImageButton

    private var correctAnswerIndex: Int = -1
    private var currentXP: Int = 0
    private var currentCoins: Int = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_habilidades)

        setupViews()
        loadSinclairData()
    }

    private fun setupViews() {
        tvSkillName = findViewById(R.id.tvSkillName)
        pbMastery = findViewById(R.id.pbMastery)
        tvSinclairText = findViewById(R.id.tvSinclairText)
        tvQuestion = findViewById(R.id.tvQuestion)
        rgOptions = findViewById(R.id.rgOptions)
        btnRespond = findViewById(R.id.btnRespond)
        tvFeedbackCoT = findViewById(R.id.tvFeedbackCoT)
        btnVoiceTutor = findViewById(R.id.btnVoiceTutor)

        btnRespond.setOnClickListener { evaluateAnswer() }
        btnVoiceTutor.setOnClickListener {
            Toast.makeText(this, "Sinclair: 'Escucha con atención la estrategia...'", Toast.LENGTH_SHORT).show()
        }
    }

    private fun loadSinclairData() {
        // Simulación de respuesta de API de Sinclair
        val mockJson = """
            {
                "skill": "Interpretar",
                "mastery": 65,
                "text": "En el corazón de la inteligencia artificial, Sinclair no solo procesa datos, sino que teje narrativas para desafiar la mente humana. La lectura no es un acto pasivo, sino una conversación entre el autor y el lector...",
                "question": "¿Cuál es la función principal de Sinclair según el texto?",
                "options": [
                    "Sustituir la lectura humana.",
                    "Procesar datos estadísticos únicamente.",
                    "Desafiar la mente humana mediante narrativas.",
                    "Automatizar la corrección de pruebas."
                ],
                "correctIndex": 2,
                "cotFeedback": "Sinclair se presenta como un creador de narrativas que busca 'desafiar la mente', lo cual va más allá del simple procesamiento de datos mencionado en la opción B."
            }
        """.trimIndent()

        processSinclairJson(mockJson)
    }

    private fun processSinclairJson(jsonString: String) {
        val json = JSONObject(jsonString)
        
        val skill = json.getString("skill")
        val mastery = json.getInt("mastery")
        val text = json.getString("text")
        val question = json.getString("question")
        val options = json.getJSONArray("options")
        correctAnswerIndex = json.getInt("correctIndex")
        val cotFeedback = json.getString("cotFeedback")

        tvSkillName.text = "Habilidad: $skill"
        pbMastery.progress = mastery
        tvSinclairText.text = text
        tvQuestion.text = question
        
        findViewById<RadioButton>(R.id.rbOptionA).text = options.getString(0)
        findViewById<RadioButton>(R.id.rbOptionB).text = options.getString(1)
        findViewById<RadioButton>(R.id.rbOptionC).text = options.getString(2)
        findViewById<RadioButton>(R.id.rbOptionD).text = options.getString(3)

        tvFeedbackCoT.text = cotFeedback
        
        startImpulsivityTimer(text.length)
    }

    /**
     * Inhibidor de Impulsividad: Bloquea el botón según la extensión del texto.
     * Estimación: ~1 segundo por cada 100 caracteres.
     */
    private fun startImpulsivityTimer(textLength: Int) {
        val secondsToWait = (textLength / 100).coerceAtLeast(3).toLong()
        btnRespond.isEnabled = false
        
        object : CountDownTimer(secondsToWait * 1000, 1000) {
            override fun onTick(millisUntilFinished: Long) {
                btnRespond.text = "Lee con calma (${millisUntilFinished / 1000}s)"
            }

            override fun onFinish() {
                btnRespond.isEnabled = true
                btnRespond.text = "Responder"
            }
        }.start()
    }

    private fun evaluateAnswer() {
        val checkedId = rgOptions.checkedRadioButtonId
        if (checkedId == -1) {
            Toast.makeText(this, "Selecciona una opción", Toast.LENGTH_SHORT).show()
            return
        }

        val selectedIndex = when (checkedId) {
            R.id.rbOptionA -> 0
            R.id.rbOptionB -> 1
            R.id.rbOptionC -> 2
            R.id.rbOptionD -> 3
            else -> -1
        }

        if (selectedIndex == correctAnswerIndex) {
            currentXP += 50
            currentCoins += 10
            Toast.makeText(this, "¡Correcto! +50 XP | +10 Monedas PAES", Toast.LENGTH_LONG).show()
            tvFeedbackCoT.visibility = View.GONE
            // Aquí podrías cargar la siguiente pregunta
        } else {
            tvFeedbackCoT.visibility = View.VISIBLE
            Toast.makeText(this, "Revisa la retroalimentación de Sinclair", Toast.LENGTH_SHORT).show()
        }
    }
}
