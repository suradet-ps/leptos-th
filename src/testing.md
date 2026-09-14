# การทดสอบคอมโพเนนต์ของคุณ

การทดสอบส่วนติดต่อผู้ใช้ (UI) อาจเป็นเรื่องที่ค่อนข้างท้าทาย แต่ก็มีความสำคัญเป็นอย่างยิ่ง บทนี้จะแนะนำหลักการและแนวทางปฏิบัติสำหรับการทดสอบแอปพลิเคชัน Leptos

## 1. ทดสอบตรรกะทางธุรกิจด้วยการทดสอบ Rust ธรรมดา

ในหลายสถานการณ์ การแยกตรรกะทางธุรกิจ (business logic) ออกมาจากตัวคอมโพเนนต์เพื่อนำไปเขียนยูนิตเทสต์แยกต่างหาก ถือเป็นแนวทางที่เหมาะสมอย่างยิ่ง สำหรับคอมโพเนนต์เรียบง่ายทั่วไปอาจไม่มีตรรกะซับซ้อนอะไรให้ต้องทดสอบ แต่สำหรับคอมโพเนนต์ที่มีการคำนวณหรือจัดการข้อมูล การห่อหุ้มข้อมูลไว้ในประเภทข้อมูลเฉพาะ (wrapper type) ที่ทดสอบได้ง่าย แล้วอิมพลีเมนต์ตรรกะเหล่านั้นไว้ในบล็อก `impl` ของ Rust ปกติ ย่อมคุ้มค่าต่อการดูแลรักษาในระยะยาว

ตัวอย่างเช่น แทนที่จะฝังตรรกะไว้ในคอมโพเนนต์โดยตรงแบบนี้:

```rust
#[component]
pub fn TodoApp() -> impl IntoView {
    let (todos, set_todos) = signal(vec![Todo { /* ... */ }]);
    // ⚠️ this is hard to test because it's embedded in the component
    let num_remaining = move || todos.read().iter().filter(|todo| !todo.completed).sum();
}
```

คุณสามารถแยกตรรกะนั้นออกมาไว้ในโครงสร้างข้อมูลต่างหาก และเขียนชุดการทดสอบกำกับไว้ได้:

```rust
pub struct Todos(Vec<Todo>);

impl Todos {
    pub fn num_remaining(&self) -> usize {
        self.0.iter().filter(|todo| !todo.completed).sum()
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn test_remaining() {
        // ...
    }
}

#[component]
pub fn TodoApp() -> impl IntoView {
    let (todos, set_todos) = signal(Todos(vec![Todo { /* ... */ }]));
    // ✅ this has a test associated with it
    let num_remaining = move || todos.read().num_remaining();
}
```

โดยทั่วไปแล้ว ยิ่งตรรกะถูกผูกติดอยู่ภายในตัวคอมโพเนนต์น้อยลงเท่าไร โค้ดของคุณก็จะยิ่งสอดคล้องกับแนวทางสำนวนที่ดีของ Rust (idiomatic Rust) มากขึ้น และทำให้เขียนชุดทดสอบได้ง่ายขึ้นตามไปด้วย

## 2. ทดสอบคอมโพเนนต์ด้วยการทดสอบแบบเอนด์ทูเอนด์ (`e2e`)

ในไดเรกทอรี [`examples`](https://github.com/leptos-rs/leptos/tree/main/examples) ของ Leptos มีตัวอย่างหลายโปรเจกต์ที่มาพร้อมชุดการทดสอบแบบเอนด์ทูเอนด์ (End-to-End หรือ E2E) อย่างครอบคลุม โดยใช้เครื่องมือทดสอบที่หลากหลาย

วิธีที่ง่ายและเห็นภาพชัดเจนที่สุดคือการเข้าไปดูตัวอย่างการเขียนชุดทดสอบจริงในรีโพ:

### `wasm-bindgen-test` กับ [`counter`](https://github.com/leptos-rs/leptos/blob/main/examples/counter/tests/web.rs)

นี่เป็นรูปแบบการตั้งค่าชุดทดสอบด้วยตนเองที่ตรงไปตรงมา โดยใช้คำสั่ง [`wasm-pack test`](https://rustwasm.github.io/wasm-pack/book/commands/test.html)

#### ตัวอย่างการทดสอบ

```rust
#[wasm_bindgen_test]
async fn clear() {
    let document = document();
    let test_wrapper = document.create_element("section").unwrap();
    let _ = document.body().unwrap().append_child(&test_wrapper);

    // start by rendering our counter and mounting it to the DOM
    // note that we start at the initial value of 10
    let _dispose = mount_to(
        test_wrapper.clone().unchecked_into(),
        || view! { <SimpleCounter initial_value=10 step=1/> },
    );

    // now we extract the buttons by iterating over the DOM
    // this would be easier if they had IDs
    let div = test_wrapper.query_selector("div").unwrap().unwrap();
    let clear = test_wrapper
        .query_selector("button")
        .unwrap()
        .unwrap()
        .unchecked_into::<web_sys::HtmlElement>();

    // now let's click the `clear` button
    clear.click();

    // the reactive system is built on top of the async system, so changes are not reflected
    // synchronously in the DOM
    // in order to detect the changes here, we'll just yield for a brief time after each change,
    // allowing the effects that update the view to run
    tick().await;

    // now let's test the <div> against the expected value
    // we can do this by testing its `outerHTML`
    assert_eq!(div.outer_html(), {
        // it's as if we're creating it with a value of 0, right?
        let (value, _set_value) = signal(0);

        // we can remove the event listeners because they're not rendered to HTML
        view! {
            <div>
                <button>"Clear"</button>
                <button>"-1"</button>
                <span>"Value: " {value} "!"</span>
                <button>"+1"</button>
            </div>
        }
        // Leptos supports multiple backend renderers for HTML elements
        // .into_view() here is just a convenient way of specifying "use the regular DOM renderer"
        .into_view()
        // views are lazy -- they describe a DOM tree but don't create it yet
        // calling .build() will actually build the DOM elements
        .build()
        // .build() returned an ElementState, which is a smart pointer for
        // a DOM element. So we can still just call .outer_html(), which access the outerHTML on
        // the actual DOM element
        .outer_html()
    });

    // There's actually an easier way to do this...
    // We can just test against a <SimpleCounter/> with the initial value 0
    assert_eq!(test_wrapper.inner_html(), {
        let comparison_wrapper = document.create_element("section").unwrap();
        let _dispose = mount_to(
            comparison_wrapper.clone().unchecked_into(),
            || view! { <SimpleCounter initial_value=0 step=1/>},
        );
        comparison_wrapper.inner_html()
    });
}
```

### [Playwright กับ `counters`](https://github.com/leptos-rs/leptos/tree/main/examples/counters/e2e)

การทดสอบส่วนนี้จะใช้เครื่องมือทดสอบฝั่ง JavaScript ยอดนิยมอย่าง Playwright เพื่อรันการทดสอบแบบ End-to-End บนตัวอย่างเดียวกัน ซึ่งมอบประสบการณ์และแนวทางการทดสอบที่คุ้นเคยเป็นอย่างดีสำหรับนักพัฒนาสายฟรอนต์เอนด์

#### ตัวอย่างการทดสอบ

```js
test.describe("Increment Count", () => {
  test("should increase the total count", async ({ page }) => {
    const ui = new CountersPage(page);
    await ui.goto();
    await ui.addCounter();

    await ui.incrementCount();
    await ui.incrementCount();
    await ui.incrementCount();

    await expect(ui.total).toHaveText("3");
  });
});
```

### [การทดสอบ Gherkin/Cucumber กับ `todo_app_sqlite`](https://github.com/leptos-rs/leptos/blob/main/examples/todo_app_sqlite/e2e/README.md)

คุณสามารถผสานรวมเครื่องมือทดสอบใด ๆ ที่คุณชื่นชอบเข้ากับเวิร์กโฟลว์นี้ได้อย่างอิสระ ตัวอย่างนี้ใช้ Cucumber ซึ่งเป็นเฟรมเวิร์กการทดสอบแบบ Behavior-Driven Development (BDD) ที่อิงข้อความภาษาธรรมชาติ

```
@add_todo
Feature: Add Todo

    Background:
        Given I see the app

    @add_todo-see
    Scenario: Should see the todo
        Given I set the todo as Buy Bread
        When I click the Add button
        Then I see the todo named Buy Bread

    # @allow.skipped
    @add_todo-style
    Scenario: Should see the pending todo
        When I add a todo as Buy Oranges
        Then I see the pending todo
```

โดยนิยามเบื้องหลังของแต่ละขั้นตอน (step definitions) จะถูกเขียนด้วยโค้ด Rust ดังนี้:

```rust
use crate::fixtures::{action, world::AppWorld};
use anyhow::{Ok, Result};
use cucumber::{given, when};

#[given("I see the app")]
#[when("I open the app")]
async fn i_open_the_app(world: &mut AppWorld) -> Result<()> {
    let client = &world.client;
    action::goto_path(client, "").await?;

    Ok(())
}

#[given(regex = "^I add a todo as (.*)$")]
#[when(regex = "^I add a todo as (.*)$")]
async fn i_add_a_todo_titled(world: &mut AppWorld, text: String) -> Result<()> {
    let client = &world.client;
    action::add_todo(client, text.as_str()).await?;

    Ok(())
}

// etc.
```

### เรียนรู้เพิ่มเติม

ขอแนะนำให้เข้าไปดูการตั้งค่า CI ในรีโพซิทอรีของ Leptos เพื่อศึกษาเพิ่มเติมเกี่ยวกับวิธีการนำเครื่องมือเหล่านี้ไปปรับใช้ในแอปพลิเคชันของคุณเอง วิธีการทดสอบทั้งหมดที่กล่าวถึงนี้ถูกใช้งานจริงและรันตรวจสอบความถูกต้องของแอปตัวอย่างใน Leptos เป็นประจำสม่ำเสมอ
